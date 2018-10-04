"""

"""


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
    import PowerOutages_V2.doit_PowerOutage_ProviderClasses as ProvMod
    import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod
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
        items = [item for item in parser[key]]

        if "BGE" in key:
            obj.soap_header_uri, obj.post_data_file, obj.post_uri = [parser[key][item] for item in items]
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_uri = [parser[key][item] for item in items]

        # print(obj.__dict__)


    # Make a metadata request and handle

    # Make a json data request and handle

    # Make BGE specific calls


if __name__ == "__main__":
    main()
