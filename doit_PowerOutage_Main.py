"""

"""


def main():
    import configparser
    # import json
    import os
    import PowerOutages_V2.doit_PowerOutage_BGEClasses as BGEMod
    import PowerOutages_V2.doit_PowerOutage_CTKClasses as CTKMod
    import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality as DbMod
    import PowerOutages_V2.doit_PowerOutage_DELClasses as DELMod
    import PowerOutages_V2.doit_PowerOutage_EUCClasses as EUCMod
    import PowerOutages_V2.doit_PowerOutage_FESClasses as FESMod
    import PowerOutages_V2.doit_PowerOutage_PEPClasses as PEPMod
    # import PowerOutages_V2.doit_PowerOutage_ProviderClasses as ProvMod
    import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod
    import PowerOutages_V2.doit_PowerOutage_TestFunctions as TestMod
    import PowerOutages_V2.doit_PowerOutage_UtilityClass as UtilMod
    # import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebMod

    # VARIABLES
    _root_project_path = os.path.dirname(__file__)
    credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
    centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
    OUTPUT_JSON_FILE = f"{_root_project_path}\JSON_Outputs\PowerOutageFeeds_StatusJSON.json"
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(filenames=[credentials_path, centralized_variables_path])
    outage_area_types = ("County", "ZIP")

    # Need to set up objects for use
    provider_objects = {"BGE_County": BGEMod.BGE("BGE"),
                        "BGE_ZIP": BGEMod.BGE("BGE"),
                        "CTK_County": CTKMod.CTK("CTK"),
                        "CTK_ZIP": CTKMod.CTK("CTK"),
                        "DEL_County": DELMod.DEL("DEL"),
                        "DEL_ZIP": DELMod.DEL("DEL"),
                        "EUC_County": EUCMod.EUC("EUC"),
                        "EUC_ZIP": EUCMod.EUC("EUC"),
                        "FES_County": FESMod.FES("FES"),
                        "FES_ZIP": FESMod.FES("FES"),
                        "PEP_County": PEPMod.PEP("PEP"),
                        "PEP_ZIP": PEPMod.PEP("PEP"),
                        "SME_County": SMEMod.SME("SME"),
                        "SME_ZIP": SMEMod.SME("SME"),
                        }

    # Need to get and store variables, as provider object attributes, from cfg file.
    for key, obj in provider_objects.items():
        section_items = [item for item in parser[key]]
        if "BGE" in key:
            obj.soap_header_uri, obj.post_uri = [parser[key][item] for item in section_items]
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_uri = [parser[key][item] for item in section_items]

    # Need to get metadata key, for those providers that use the metadata key to access the data feed.
    for key, obj in provider_objects.items():
        if obj.metadata_feed_uri == "NA" or obj.metadata_feed_uri is None:
            # Providers who do not use the metadata key style. Also, BGE does not use a GET request; Uses POST.
            continue
        else:
            obj.metadata_feed_response = obj.web_func_class.make_web_request(uri=obj.metadata_feed_uri)

    # Need to extract the metadata key and assign to provider object attribute for later use.
    for key, obj in provider_objects.items():
        if obj.metadata_feed_uri == "NA" or obj.metadata_feed_uri is None:
            continue
        else:
            if "xml" in obj.metadata_feed_response.headers["content-type"]:
                metadata_xml_element = obj.prov_xml_class.parse_xml_response_to_element(
                    response_xml_str=obj.metadata_feed_response.text)
                obj.metadata_key = obj.prov_xml_class.extract_metadata_attribute_value_from_xml_element(
                    root_element=metadata_xml_element)
            else:
                metadata_response_dict = obj.metadata_feed_response.json()
                obj.metadata_key = obj.prov_json_class.extract_attribute_from_dict(
                    metadata_dict=metadata_response_dict,
                    attribute_name=obj.metadata_key_attribute)

    # Need to make the data feed requests and store the response.
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
            if obj.metadata_key is None:
                obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)
            else:
                obj.data_feed_uri = obj.build_data_feed_uri(metadata_key=obj.metadata_key,
                                                            data_feed_uri=obj.data_feed_uri)
                obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)

    # Need to write json file containing status check on all feeds.
    # TODO: Will need to be moved to later stage when finish coding check for data freshness also
    status_check_output_dict = {}
    for key, obj in provider_objects.items():
        obj.set_status_codes()
    for key, obj in provider_objects.items():
        print(key, obj.data_feed_response_status_code, obj.date_created_response_status_code, obj.metadata_feed_response_status_code)
        status_check_output_dict.update(obj.build_output_dict(unique_key=key))
    UtilMod.Utility.write_to_file(file=OUTPUT_JSON_FILE, content=status_check_output_dict)

    # FIXME: The date created doesn't seem to be populating in json file. Is always null.

    # TODO: Using response content, extract the outage data for each provider. Each provider does it differently
    # NOTE: STARTING WITH FES AS MY MODEL SINCE IT IS SIMPLE

    # Need to extract the outage data for each provider from the response.
    #   establish connection
    db_obj = DbMod.DatabaseUtilities(parser=parser)
    # db_obj.establish_database_connection()  # TODO: Try this on MEMA box to see if connection code works.

    #   parse xml to dom
    # STOPPED
    #   trigger stored procedure for deleting, then commit
    #   get the outage count
    #   for each outage get
    #       customer count
    #       county
    #       state
    #   trigger stored procedure for updating, then commit






    # TESTING CALLS
    exit()
    TestMod.check_metadata_uri_presence_against_key_presence(obj_dict=provider_objects)


if __name__ == "__main__":
    main()
