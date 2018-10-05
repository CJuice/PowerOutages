"""

"""


def main():
    import configparser
    import json
    import os
    import PowerOutages_V2.doit_PowerOutage_BGEClasses as BGEMod
    import PowerOutages_V2.doit_PowerOutage_CTKClasses as CTKMod
    # import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality as DbMod
    import PowerOutages_V2.doit_PowerOutage_DELClasses as DELMod
    import PowerOutages_V2.doit_PowerOutage_EUCClasses as EUCMod
    import PowerOutages_V2.doit_PowerOutage_FESClasses as FESMod
    import PowerOutages_V2.doit_PowerOutage_PEPClasses as PEPMod
    # import PowerOutages_V2.doit_PowerOutage_ProviderClasses as ProvMod
    import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod
    import PowerOutages_V2.doit_PowerOutage_TestFunctions as TestMod
    # import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebMod

    # VARIABLES
    _root_project_path = os.path.dirname(__file__)
    credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
    centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(filenames=["doit_PowerOutage_Credentials.cfg", "doit_PowerOutage_CentralizedVariables.cfg"])
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
    #   Need to get and store variables
    for key, obj in provider_objects.items():
        section_items = [item for item in parser[key]]
        if "BGE" in key:
            obj.soap_header_uri, obj.post_data_file, obj.post_uri = [parser[key][item] for item in section_items]
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_uri = [parser[key][item] for item in section_items]

    # Need to get metadata key, for those providers that use the metadata key style
    for key, obj in provider_objects.items():
        if "BGE" in key:
            # BGE does not use the metadata key style AND it does not use a GET request; Uses POST. 20181005 CJuice
            continue
        else:
            if obj.metadata_feed_uri == "NA":
                continue
            else:
                obj.metadata_feed_response = obj.web_func_class.make_web_request(uri=obj.metadata_feed_uri)

    # Need to extract the metadata key and assign to object attribute for later use
    for key, obj in provider_objects.items():
        if obj.metadata_feed_uri == "NA" or obj.metadata_feed_uri is None:
            continue
        else:
            if "xml" in obj.metadata_feed_response.headers["content-type"]:
                metadata_xml_element = obj.prov_xml_class.parse_xml_response_to_element(response_xml_str=obj.metadata_feed_response.text)
                obj.metadata_key = obj.prov_xml_class.extract_metadata_attribute_value_from_xml_element(root_element=metadata_xml_element)

            else:
                metadata_response_dict = obj.metadata_feed_response.json()
                obj.metadata_key = obj.prov_json_class.extract_attribute_from_dict(metadata_dict=metadata_response_dict,
                                                                                   attribute_name=obj.metadata_key_attribute)

    # Need to make the data feed request and

    # Make BGE specific calls


    # TESTING FUNCTION CALLS
    exit()
    TestMod.check_metadata_uri_presence_against_key_presence(obj_dict=provider_objects)


if __name__ == "__main__":
    main()
