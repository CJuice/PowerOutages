"""

"""
# TODO: Add logging functionality at some level for this process


def main():
    import configparser
    import os
    import PowerOutages_V2.doit_PowerOutage_BGEClasses as BGEMod
    import PowerOutages_V2.doit_PowerOutage_CTKClasses as CTKMod
    import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality as DbMod
    import PowerOutages_V2.doit_PowerOutage_DELClasses as DELMod
    import PowerOutages_V2.doit_PowerOutage_EUCClasses as EUCMod
    import PowerOutages_V2.doit_PowerOutage_FESClasses as FESMod
    import PowerOutages_V2.doit_PowerOutage_PEPClasses as PEPMod
    import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod
    from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL

    # VARIABLES
    _root_project_path = os.path.dirname(__file__)
    centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
    credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
    none_and_not_available = (None, "NA")
    OUTPUT_JSON_FILE = f"{_root_project_path}\JSON_Outputs\PowerOutageFeeds_StatusJSON.json"
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(filenames=[credentials_path, centralized_variables_path])

    # Need to set up provider objects for use. Later referred to as "key, obj" in iteration loops.
    provider_objects = {"BGE_County": BGEMod.BGE(provider_abbrev="BGE", style=DOIT_UTIL.COUNTY),
                        "BGE_ZIP": BGEMod.BGE(provider_abbrev="BGE", style=DOIT_UTIL.ZIP),
                        "CTK_County": CTKMod.CTK(provider_abbrev="CTK", style=DOIT_UTIL.COUNTY),
                        "CTK_ZIP": CTKMod.CTK(provider_abbrev="CTK", style=DOIT_UTIL.ZIP),
                        "DEL_County": DELMod.DEL(provider_abbrev="DEL", style=DOIT_UTIL.COUNTY),
                        "DEL_ZIP": DELMod.DEL(provider_abbrev="DEL", style=DOIT_UTIL.ZIP),
                        "EUC_County": EUCMod.EUC(provider_abbrev="EUC", style=DOIT_UTIL.COUNTY),
                        "EUC_ZIP": EUCMod.EUC(provider_abbrev="EUC", style=DOIT_UTIL.ZIP),
                        "FES_County": FESMod.FES(provider_abbrev="FES", style=DOIT_UTIL.COUNTY),
                        "FES_ZIP": FESMod.FES(provider_abbrev="FES", style=DOIT_UTIL.ZIP),
                        "PEP_County": PEPMod.PEP(provider_abbrev="PEP", style=DOIT_UTIL.COUNTY),
                        "PEP_ZIP": PEPMod.PEP(provider_abbrev="PEP", style=DOIT_UTIL.ZIP),
                        "SME_County": SMEMod.SME(provider_abbrev="SME", style=DOIT_UTIL.COUNTY),
                        "SME_ZIP": SMEMod.SME(provider_abbrev="SME", style=DOIT_UTIL.ZIP),
                        }

    # Need to get and store variables, as provider object attributes, from cfg file.
    print("Gathering variables...")
    for key, obj in provider_objects.items():
        section_items = [item for item in parser[key]]
        if "BGE" in key:
            obj.soap_header_uri, obj.post_uri = [parser[key][item] for item in section_items]
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_feed_uri = [parser[key][item] for item in section_items]

    # Need to make the metadata key requests, for those providers that use the metadata key, and store the response.
    #   Key used in the uri for accessing the data feeds and date created feeds.
    print("Metadata feed processing...")
    for key, obj in provider_objects.items():
        if obj.metadata_feed_uri in none_and_not_available:
            # Providers who do not use the metadata key style. Also, BGE does not use a GET request; Uses POST.
            continue
        else:
            obj.metadata_feed_response = obj.web_func_class.make_web_request(uri=obj.metadata_feed_uri)

    # Need to extract the metadata key and assign to provider object attribute for later use.
    for key, obj in provider_objects.items():
        if obj.metadata_feed_uri in none_and_not_available:
            continue
        else:
            if "xml" in obj.metadata_feed_response.headers["content-type"]:
                metadata_xml_element = DOIT_UTIL.parse_xml_response_to_element(
                    response_xml_str=obj.metadata_feed_response.text)
                obj.metadata_key = DOIT_UTIL.extract_attribute_value_from_xml_element_by_index(
                    root_element=metadata_xml_element)
            else:
                metadata_response_dict = obj.metadata_feed_response.json()
                obj.metadata_key = DOIT_UTIL.extract_attribute_from_dict(
                    data_dict=metadata_response_dict,
                    attribute_name=obj.metadata_key_attribute)

    # Need to make the date created requests, for providers with a date created service, and store the response.
    print("Date Generated feed processing...")
    for key, obj in provider_objects.items():
        if obj.date_created_feed_uri in none_and_not_available:
            continue
        else:
            obj.date_created_feed_uri = DOIT_UTIL.build_feed_uri(metadata_key=obj.metadata_key,
                                                                 data_feed_uri=obj.date_created_feed_uri)
            obj.date_created_feed_response = obj.web_func_class.make_web_request(uri=obj.date_created_feed_uri)

    # Need to extract the date created value and assign to provider object attribute
    for key, obj in provider_objects.items():
        if obj.date_created_feed_uri in none_and_not_available:
            continue
        else:
            if "xml" in obj.date_created_feed_response.headers["content-type"]:
                date_created_xml_element = DOIT_UTIL.parse_xml_response_to_element(
                    response_xml_str=obj.date_created_feed_response.text)
                obj.date_created = DOIT_UTIL.extract_attribute_value_from_xml_element_by_index(
                    root_element=date_created_xml_element)
            else:
                date_created_response_dict = obj.date_created_feed_response.json()
                if obj.abbrev == "SME":
                    # 20181010 CJuice, All providers except SME use "file_data" as the key to access the data dict
                    #   containing the date. SME uses "summaryFileData" as the key to access the data dict
                    #   containing the date.
                    file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=date_created_response_dict,
                                                                      attribute_name="summaryFileData")
                else:
                    file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=date_created_response_dict,
                                                                      attribute_name="file_data")
                obj.date_created = DOIT_UTIL.extract_attribute_from_dict(
                    data_dict=file_data,
                    attribute_name=obj.date_created_attribute)

    # Need to make the data feed requests and store the response.
    print("Data feed processing...")
    for key, obj in provider_objects.items():
        if "BGE" in key:
            # BGE uses POST and no metadata key.
            # Make the POST request and include the headers and the post data as a string (is xml, not json)
            bge_extra_header = obj.build_extra_header_for_SOAP_request()
            bge_username, bge_password = [parser["BGE"][item] for item in parser["BGE"]]
            obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.post_uri,
                                                                         payload=obj.POST_DATA_XML_STRING.format(
                                                                             username=bge_username,
                                                                             password=bge_password),
                                                                         style="POST_data",
                                                                         headers=bge_extra_header)
        else:
            if obj.metadata_key in none_and_not_available:
                obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)
            else:
                obj.build_feed_uri()
                obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)

    # Need to detect the style of response
    for key, obj in provider_objects.items():
        obj.detect_response_style()

    # Need to extract the outage data from the response, for each provider. Where applicable, extract the
    #   date created/generated. Some providers provide the date created/generated value in the data feed.
    print("Data processing...")
    for key, obj in provider_objects.items():
        if key in ("FES_County",):
            obj.extract_maryland_dict_from_county_response()
            obj.extract_outage_counts_by_county()
            obj.purge_duplicate_stats_objects()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.change_case_to_title(stats_objects=obj.stats_objects)

        elif key in ("FES_ZIP",):
            obj.extract_events_from_zip_response()
            obj.extract_outage_counts_by_zip()
            obj.purge_duplicate_stats_objects()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            obj.process_customer_counts_to_integers()

        elif key in ("DEL_County", "PEP_County"):
            obj.extract_areas_list_county_process()
            obj.extract_county_outage_lists_by_state()
            obj.extract_outage_counts_by_county()
            obj.purge_duplicate_stats_objects()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)

        elif key in ("DEL_ZIP", "PEP_ZIP"):
            obj.extract_zip_descriptions_list()
            obj.extract_outage_counts_by_zip_desc()
            obj.purge_duplicate_stats_objects()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)

        elif key in ("SME_County", "SME_ZIP"):
            obj.extract_outage_events_list()
            obj.extract_outage_counts_by_desc()
            obj.purge_duplicate_stats_objects()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.change_case_to_title(stats_objects=obj.stats_objects)

        elif key in ("EUC_County", "EUC_ZIP"):
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_outage_events_list_from_xml_str()
            obj.extract_outage_counts()
            obj.purge_duplicate_stats_objects()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)

        elif key in ("CTK_County", "CTK_ZIP"):
            # TODO: CTK company feed appears to not contain any data when no outages are present. This means there are
            #   TODO: no values to show, rather than a zero value. So, database will have no CTK records when count=0
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_report_by_id()
            obj.extract_outage_dataset()
            obj.extract_outage_counts_from_dataset()
            obj.purge_duplicate_stats_objects()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)

        elif key in ("BGE_County", "BGE_ZIP"):
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_outage_elements()
            obj.extract_outage_counts()
            obj.purge_duplicate_stats_objects()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)

        # Need to groom the date created values, and calculate the data age for each provider
        obj.groom_date_created()
        obj.calculate_data_age_minutes()

        # for j in obj.stats_objects:
        #     print(j)

    # Need to write json file containing status check on all feeds.
    print("Writing feed check to json file...")
    status_check_output_dict = {}
    for key, obj in provider_objects.items():
        obj.set_status_codes()
    for key, obj in provider_objects.items():
        status_check_output_dict.update(obj.build_output_dict(unique_key=key))
    DOIT_UTIL.write_to_file(file=OUTPUT_JSON_FILE, content=status_check_output_dict)

    #   Need to prepare for database transactions and establish a connection.
    print("Database operations initiated...")
    db_obj = DbMod.DatabaseUtilities(parser=parser)
    db_obj.create_database_connection_string()
    db_obj.establish_database_connection()

    # For every provider object need to delete existing records, and update with new. Need a cursor to do so.
    for key, obj in provider_objects.items():
        db_obj.create_database_cursor()

        # Need to delete existing records from database table for every/all provider. All the same WRT delete.
        db_obj.delete_records(style=obj.style, provider_abbrev=obj.abbrev)

        # Need to update database table with new records and handle unique provider functionality
        if key in ("CTK_ZIP",):
            obj.create_grouped_zipcodes_dict(cursor=db_obj.cursor)

        try:
            insert_generator = obj.generate_insert_sql_statement()
            for sql_statement in insert_generator:
                db_obj.insert_record_into_database(sql_statement=sql_statement)

        except TypeError as te:
            print(f"TypeError. {obj.abbrev} appears to have no stats objects. \n{te}")

        else:
            db_obj.commit_changes()
            print(f"Records inserted: {obj.abbrev}  {obj.style} {len(obj.stats_objects)}")

        finally:
            # Need to clean up for next provider
            db_obj.delete_cursor()

    print("Process complete.")


if __name__ == "__main__":
    main()
