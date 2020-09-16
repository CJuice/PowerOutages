
def main():
    import os
    features_list = [r"doit_PowerOutage_ArchiveClasses.py",
                     r"doit_PowerOutage_BGEClasses.py",
                     r"doit_PowerOutage_CentralizedVariables.py",
                     r"doit_PowerOutage_Credentials.cfg",
                     r"doit_PowerOutage_CTKClasses.py",
                     r"doit_PowerOutage_CustomerClass.py",
                     r"doit_PowerOutage_DatabaseFunctionality.py",
                     r"doit_PowerOutage_DELClasses.py",
                     r"doit_PowerOutage_EUCClasses.py",
                     r"doit_PowerOutage_FESClasses.py",
                     r"doit_PowerOutage_Main.py",
                     r"doit_PowerOutage_PEPClasses.py",
                     r"doit_PowerOutage_Kubra_ParentClass.py",
                     r"doit_PowerOutage_ProviderClasses.py",
                     r"doit_PowerOutage_ProviderURI.cfg",
                     r"doit_PowerOutage_SMEClasses.py",
                     r"doit_PowerOutage_UtilityClass.py",
                     r"doit_PowerOutage_WebRelatedFunctionality.py",
                     r"JSON_Outputs",
                     ]
    for item in features_list:
        try:
            assert(os.path.exists(item))
        except AssertionError as ae:
            print(f"Assertion Error: {item}")
        else:
            # print(f"{item} passed")
            continue

    print("Assertion Tests Complete")


if __name__ == "__main__":
    main()
