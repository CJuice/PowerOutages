"""
For manually executing record deletion in Open Data Portal assets.
Initially built to reduce the time interval represented in the Open Data Portal assets. They were initially
accumulated for up to 30 days during development. For production, the time window was reduced to 21 days. Only
2 weeks worth are needed on the power outage web application graphs but an extra week is kept in case the process
encounters issues. The extra data will provide a buffer for visualization until the process is restored. The
functionality is identical to that in the production process, just extracted for an independent tool.

"""


def main():

    from PowerOutages.doit_PowerOutage_CloudStorageFunctionality import OpenData
    from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
    import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS
    import os

    # VARIABLES
    credentials_cfg_path = os.path.join(VARS._root_project_path, VARS.credentials_cfg_file)
    DOIT_UTIL.PARSER.read(filenames=[credentials_cfg_path, ])

    print("OPEN DATA PORTAL")
    open_data = OpenData(parser=DOIT_UTIL.PARSER)

    # Overwrite the default constant value for this manual deletion effort
    OpenData.RECORD_DELETION_AGE_LIMIT_DAYS = 21

    open_data.create_socrata_client()

    print(
        f"Deleting aged records ({OpenData.RECORD_DELETION_AGE_LIMIT_DAYS} days) in Open Data assets...{DOIT_UTIL.current_date_time_str()}")
    county_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["COUNTY_4X4"])
    zip_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["ZIP_4X4"])
    status_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["STATUS_4X4"])

    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["COUNTY_4X4"],
                                    results_gen=county_records_gen)
    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["ZIP_4X4"],
                                    results_gen=zip_records_gen)
    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["STATUS_4X4"],
                                    results_gen=status_records_gen)
    print(f"Process Completed...{DOIT_UTIL.current_date_time_str()}")


if __name__ == "__main__":
    main()