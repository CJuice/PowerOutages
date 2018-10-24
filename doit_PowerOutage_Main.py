"""

"""
# TODO: Add logging functionality at some level for this process

def main():
    import configparser
    import os
    import pprint
    import PowerOutages_V2.doit_PowerOutage_BGEClasses as BGEMod
    import PowerOutages_V2.doit_PowerOutage_CTKClasses as CTKMod
    import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality as DbMod
    import PowerOutages_V2.doit_PowerOutage_DELClasses as DELMod
    import PowerOutages_V2.doit_PowerOutage_EUCClasses as EUCMod
    import PowerOutages_V2.doit_PowerOutage_FESClasses as FESMod
    import PowerOutages_V2.doit_PowerOutage_PEPClasses as PEPMod
    import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod
    import PowerOutages_V2.doit_PowerOutage_TestFunctions as TestMod
    from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
    # import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebMod

    # VARIABLES
    _root_project_path = os.path.dirname(__file__)
    county_style = "County"
    credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
    centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
    none_and_not_available = (None, "NA")
    OUTPUT_JSON_FILE = f"{_root_project_path}\JSON_Outputs\PowerOutageFeeds_StatusJSON.json"
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(filenames=[credentials_path, centralized_variables_path])
    pp = pprint.PrettyPrinter(indent=4)
    zip_style = "ZIP"

    # Need to set up objects for use
    provider_objects = {"BGE_County": BGEMod.BGE(provider_abbrev="BGE", style=county_style),
                        "BGE_ZIP": BGEMod.BGE(provider_abbrev="BGE", style=zip_style),
                        "CTK_County": CTKMod.CTK(provider_abbrev="CTK", style=county_style),
                        "CTK_ZIP": CTKMod.CTK(provider_abbrev="CTK", style=zip_style),
                        "DEL_County": DELMod.DEL(provider_abbrev="DEL", style=county_style),
                        "DEL_ZIP": DELMod.DEL(provider_abbrev="DEL", style=zip_style),
                        "EUC_County": EUCMod.EUC(provider_abbrev="EUC", style=county_style),
                        "EUC_ZIP": EUCMod.EUC(provider_abbrev="EUC", style=zip_style),
                        "FES_County": FESMod.FES(provider_abbrev="FES", style=county_style),
                        "FES_ZIP": FESMod.FES(provider_abbrev="FES", style=zip_style),
                        "PEP_County": PEPMod.PEP(provider_abbrev="PEP", style=county_style),
                        "PEP_ZIP": PEPMod.PEP(provider_abbrev="PEP", style=zip_style),
                        "SME_County": SMEMod.SME(provider_abbrev="SME", style=county_style),
                        "SME_ZIP": SMEMod.SME(provider_abbrev="SME", style=zip_style),
                        }

    # Need to get and store variables, as provider object attributes, from cfg file.
    print("Gathering variables...")
    for key, obj in provider_objects.items():
        section_items = [item for item in parser[key]]
        if "BGE" in key:
            obj.soap_header_uri, obj.post_uri = [parser[key][item] for item in section_items]
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_feed_uri = [parser[key][item] for item in section_items]

    # Need to make the metadata key requests and store the response, for those providers that use the metadata key.
    #   Key used to access the data feeds and date created feeds.
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
                    # 20181010 CJuice, All providers except SME use "file_data" as the key to access the data
                    #   dict containing the date. SME uses "summaryFileData" as the key to access the data dict
                    #   containing the date
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
                obj.data_feed_uri = obj.build_feed_uri(metadata_key=obj.metadata_key,
                                                       data_feed_uri=obj.data_feed_uri)
                obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)
    # Need to detect style of response
    for key, obj in provider_objects.items():
        obj.detect_response_style()

    # Need to extract the outage data for each provider from the response. Where applicable, extract the
    #   date created/generated
    print("Data processing...")
    for key, obj in provider_objects.items():
        # TODO: See what parts of below repeating code can be abstracted and performed once for all providers
        print(key, obj.data_feed_response_style)
        if key in ("FES_County",):
            continue
            obj.extract_maryland_dict_from_county_response()
            obj.extract_outage_counts_by_county()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.change_case_to_title(stats_objects=obj.stats_objects)
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("FES_ZIP",):
            continue
            obj.extract_events_from_zip_response()
            obj.extract_outage_counts_by_zip()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            obj.process_customer_counts_to_integers()
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("DEL_County", "PEP_County"):
            continue
            obj.extract_areas_list_county_process(data_json=obj.data_feed_response.json())
            obj.extract_county_outage_lists_by_state()
            obj.extract_outage_counts_by_county()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("DEL_ZIP", "PEP_ZIP"):
            continue
            obj.extract_zip_descriptions_list(data_json=obj.data_feed_response.json())
            obj.extract_outage_counts_by_zip_desc()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("SME_County", "SME_ZIP"):
            continue
            obj.extract_outage_events_list(data_json=obj.data_feed_response.json())
            obj.extract_outage_counts_by_desc()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.change_case_to_title(stats_objects=obj.stats_objects)
            # TODO: SME has some unique code for sql statement generation. That will need to be reproduced
            #   SME: Execute delete sql statement for existing records, not a stored procedure call
            #   if data exists, then map and build sql statement
            # TODO: Update task tracking table with created date. May need to do this to more than just SME ???
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("EUC_County", "EUC_ZIP"):
            continue
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_outage_events_list_from_xml_str(content_list_as_str=obj.xml_element.text)
            obj.extract_outage_counts()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            # TODO: Assess the customer count tracking functionality. Don't see in any other script.
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage

        elif key in ("CTK_County", "CTK_ZIP"):
            # TODO: CTK appears to not write any data when no outages are present. This means no zero values. The database wouldn't be updated when outages are resolved.
            continue
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_report_by_id(id=obj.style)
            obj.extract_outage_dataset()
            obj.extract_outage_counts_from_dataset()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: CTK has some unique code for sql statement generation. That will need to be reproduced
            pass

        elif key in ("BGE_County", "BGE_ZIP"):
            continue
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_outage_elements()
            obj.extract_outage_counts()
            obj.extract_date_created()
            DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
            DOIT_UTIL.process_outage_counts_to_integers(objects_list=obj.stats_objects)
            DOIT_UTIL.revise_county_name_spellings_and_punctuation(obj.stats_objects)
            for j in obj.stats_objects:
                pp.pprint(j)
            # TODO: At this point the data is ready for the database stage
        else:
            pass

    # Need to write json file containing status check on all feeds.
    print("Writing feed check to json file...")
    status_check_output_dict = {}
    for key, obj in provider_objects.items():
        obj.set_status_codes()
    for key, obj in provider_objects.items():
        status_check_output_dict.update(obj.build_output_dict(unique_key=key))
    DOIT_UTIL.write_to_file(file=OUTPUT_JSON_FILE, content=status_check_output_dict)

    # Database actions
    #   establish connection
    db_obj = DbMod.DatabaseUtilities(parser=parser)   # TODO
    db_obj.create_database_connection_string()    # TODO
    db_obj.establish_database_connection()    # TODO


    # For all providers, trigger stored procedure for deleting, then commit
    for key, obj in provider_objects.items():
        print(obj.abbrev)
        # db_obj.create_database_cursor()

        # For TESTING Purposes. Using a SELECT statement in place of DELETE statement
        # db_obj.select_records(style=obj.style, provider_abbrev=obj.abbrev)
        # db_obj.fetch_all_from_selection()
        # for row in db_obj.selection:
        #     print(row)

        # Delete existing records from database table
        # db_obj.delete_records(style=obj.style, provider_abbrev=obj.abbrev)

        # Update database table with new records
        try:
            for data_obj in obj.stats_objects:
                print("\t", data_obj)
                # TODO: Provider specific SQL Statement generation for inserting records
        except TypeError as te:
            print(f"{obj.abbrev} appears to have no stats objects: {obj.stats_objects}")

        # Clean up for next provider
        db_obj.delete_cursor()



    # TODO: Think about how to implement the delete and insert to include uniqueness of certain providers

    # trigger stored procedure for updating, then commit

    # TESTING CALLS
    exit()
    TestMod.check_metadata_uri_presence_against_key_presence(obj_dict=provider_objects)


if __name__ == "__main__":
    main()
