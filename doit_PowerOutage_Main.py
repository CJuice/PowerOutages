"""

"""


def main():
    import os
    import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality
    import PowerOutages_V2.doit_PowerOutage_ProviderClasses
    import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality

    _root_project_path = os.path.dirname(__file__)
    credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
    centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")


if __name__ == "__main__":
    main()
