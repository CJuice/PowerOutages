"""
Inspect the SME County data feed over a range of time beginning with any metadata key of interest and output spreadsheet
Inspect the SME County power outage data feed over a range of time that you specify. The start date is defined by
the metadata key that you specify and represents the youngest value to be requested. The process will begin the youngest
and work backwords in time by 30 minute increments. The span of the window of time inspected is controlled by the
integer for the number of 30 minute increments. Metadata keys are generated off the original value minus 30 minute
increments for the number of increments desired. The metadata keys are placed in the data feed url to which requests
are made. The response json is interrogated for values of interest. The output spreadsheet contains a datetime stamp in
UTC zero, adjusted time for EST, http response code, names of counties with outages, and the data feed URL used in the
request.
This process was designed to troubleshoot. SME covers Calvert, Charles, and St. Mary's counties but St. Mary's outage
values have not been detected for many weeks. To solve the problem, if it lies in the power outage python code
interrogation of the response json, response json for St. Mary's county outage is needed. This process revealed that
no St. Mary's county outages have been reported for weeks. This process could be used at any time to interrogate the
data feed. It could also be easily adapted to other power provider data feeds that are json style.
Author: CJuice
Date Created: 20190301
Revisions:
"""


def main():

    # IMPORTS
    from dateutil.parser import parse
    from datetime import datetime
    from datetime import timedelta
    from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
    import numpy as np
    import os
    import pandas as pd
    import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS
    import requests

    # VARIABLES
    _root_project_path = os.path.dirname(__file__)
    centralized_variables_path = os.path.join(_root_project_path, VARS.provider_uri_cfg_file)
    headers = ["index", "UTC DateTime", "EST DateTime", "Response Code", "Area(s)", "Data Feed URL"]
    master_list = []
    metadata_key_for_start_time_of_interest = '2019_03_01_20_13_30'     # This is the value you will want to revise
    null_areas = [np.NaN]
    number_of_30minute_increments = 10  # This value controls how far back in time the analysis looks
    output_file_path = r"testing_datafeedjson_inspector.xlsx"
    DOIT_UTIL.PARSER.read(filenames=[centralized_variables_path])

    # FUNCTIONS
    def create_full_date_time_string(value):
        """
        Take the provided metadata key in SME format, convert to str formatted for parsing by dateutil.parser.parse
        :param value: metadata key in SME style YYYY_MM_DD_HH_MM_SS
        :return: string in datetime format that dateutil.parser.parse recognizes
        """
        start_time_parts_list = value.split("_")
        date_str = "-".join(start_time_parts_list[0:3])
        time_str = ":".join(start_time_parts_list[3:])
        return " ".join([date_str, time_str])

    # FUNCTIONALITY
    full_dt_string = create_full_date_time_string(metadata_key_for_start_time_of_interest)
    metadata_datetime_of_interest = parse(full_dt_string)
    timezone_adjusted_readable_datetime_of_interest = metadata_datetime_of_interest - timedelta(days=0, hours=5,
                                                                                                minutes=0)
    for index_value in range(number_of_30minute_increments):
        metadata_datetime_of_interest -= timedelta(days=0, hours=0, minutes=30)
        timezone_adjusted_readable_datetime_of_interest -= timedelta(days=0, hours=0, minutes=30)
        metadata_key = datetime.strftime(metadata_datetime_of_interest, "%Y_%m_%d_%H_%M_%S")
        data_feed_url = DOIT_UTIL.PARSER["SME_County"]["data_feed_uri"].format(metadata_key=metadata_key)
        response = requests.get(data_feed_url)
        current_product = [index_value, metadata_datetime_of_interest, timezone_adjusted_readable_datetime_of_interest, response.status_code]

        if response.status_code == 200:
            resp_json = response.json()
            try:
                file_data = resp_json['file_data']
            except KeyError as ke:
                pass
            else:
                if len(file_data) > 0:
                    area_list = []
                    for dictionary in file_data:
                        area_list.append(dictionary['id'])
                    areas_list_string = ";".join(area_list)
                    current_product.append([areas_list_string])
                    current_product.append(data_feed_url)
                else:
                    current_product.extend([null_areas, data_feed_url])
        else:
            current_product.extend([null_areas, data_feed_url])

        current_prod_dict = dict(zip(headers, current_product))
        current_df = pd.DataFrame(data=current_prod_dict)
        master_list.append(current_df)

    df = pd.concat(objs=master_list).set_index(keys=["index"], drop=True)

    with pd.ExcelWriter(output_file_path) as xlsx_writer:
        df.to_excel(excel_writer=xlsx_writer,
                    sheet_name="Data Feed Analysis",
                    na_rep=np.NaN,
                    header=True,
                    index=False)

    print("Process completed")


if __name__ == "__main__":
    main()
