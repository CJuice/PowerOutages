
def main():
    import os
    features_list = [r"doit_PowerOutage_CentralizedVariables.cfg",
                     r"doit_PowerOutage_Credentials.cfg",
                     r"doit_PowerOutage_DatabaseFunctionality.py",
                     r"doit_PowerOutage_Main.py",
                     r"doit_PowerOutage_ProviderClasses.py",
                     r"doit_PowerOutage_WebRelatedFunctionality.py",
                     ]
    for item in features_list:
        try:
            assert(os.path.exists(item))
        except AssertionError as ae:
            print(f"Assertion Error: {item}")

    print("Assertion Tests Complete")


if __name__ == "__main__":
    main()
