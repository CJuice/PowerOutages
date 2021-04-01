"""
Classes for data preparation and cloud storage.
CloudStorage is a class for data preparation
OpenData is a class for Socrata open data portal platform specific functionality
ArcGISOnline is a class for ArcGIS Online specific functionality
Created: November 2020
Author: CJuice
Revisions:
    20210316, CJuice, Added OpenData and ArcGISOnline classes for platform specific functionality.
    20210401, CJuice, Added Open Data record deletion functionality for cleanup of records older than set limit
"""


from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS
import datetime
from sodapy import Socrata
import arcgis
import configparser
import dataclasses
import pandas as pd
import time
import types
import requests.exceptions as req_exc


class CloudStorage:
    """
    For processing outage data prior to platform specific needs.
    """

    def __init__(self):
        self.county_outage_records_df = None
        self.county_zipper = None
        self.feed_status_df = None
        self.feed_status_zipper = None
        self.grouped_sums_df = None
        self.master_groupby_area = None
        self.master_outages_df = None
        self.outages_as_record_dicts_list = []
        self.cloud_acceptable_process_run_dt_str = None
        self.zipcode_outage_records_df = None
        self.zipcode_zipper = None

    def calculate_county_outage_percentage(self) -> None:
        """
        Calculate the outage percentage for each county using the outage counts and customer counts, multiplied by 100
        :return: None
        """
        self.county_outage_records_df["percent_out"] = self.county_outage_records_df.loc[:, "outages"] / self.county_outage_records_df.loc[:, "customers"] * 100
        return None

    def correct_status_created_dt(self) -> None:
        """
        Replace space with 'T' so that Socrata will accept/recognize the datetime values as that type instead of text
        :return: None
        """
        self.feed_status_df["created"] = self.feed_status_df["created"].str.replace(" ", "T")
        return None

    def create_dt_stamp_column(self, dataframe: pd.DataFrame) -> None:
        """
        Create and set the datetime stamp column to the Socrata acceptable value
        :param dataframe: pandas dataframe
        :return: None
        """
        dataframe[VARS.date_time_field_name] = self.cloud_acceptable_process_run_dt_str
        return None

    def create_feed_status_dataframe(self, status_check_output: dict) -> None:
        """
        Create a pandas dataframe from a dict of provider feed status checks.
        Function creates dataframe, transposes data, resets index, and renames column before returning.
        :param status_check_output: dict of feed status check information
        :return: None
        """
        self.feed_status_df = pd.DataFrame(data=status_check_output).transpose().reset_index().rename(columns={"index": "prov_style"})
        return None

    @staticmethod
    def create_lists_of_record_dicts(dataframe: pd.DataFrame) -> list:
        """
        Create list of record data from record dataframes.
        For upsert payload to socrata open data portal.
        :param dataframe: pandas dataframe
        :return: list of dict records
        """
        return dataframe.to_dict(orient="records")

    def create_master_outage_dataframe(self) -> None:
        """
        Create pandas dataframe from list of outage dicts
        :return: None
        """
        self.master_outages_df = pd.DataFrame.from_records(data=self.outages_as_record_dicts_list,
                                                           columns=["style", "area", "outages", "customers"])
        return None

    def create_outage_records(self, provider_objects: dict) -> None:
        """
        Create a list of outage record dicts from the provider objects
        :param provider_objects: dict of provider objects
        :return: None
        """
        for obj in provider_objects.values():
            self.outages_as_record_dicts_list.extend([dataclasses.asdict(stat_obj) for stat_obj in obj.stats_objects])
        return None

    def create_unique_id_feed_status(self) -> None:
        """
        Combine provider style key with socrata acceptable datetime string to make a record unique id for feed status
        NOTE: Socrata unique id will be accepted with spaces " " but when attempt to delete based on a unique id
        with space in the id you get a 500 internal server error.
        :return: None
        """
        self.feed_status_df["uid"] = self.feed_status_df["prov_style"].str.replace(" ", "_") + self.cloud_acceptable_process_run_dt_str
        return None

    def create_unique_id_outages(self) -> None:
        """
        Combine area value with socrata acceptable datetime string to make a record unique id for group sums
        NOTE: Socrata unique id will be accepted with spaces " " but when attempt to delete based on a unique id
        with space in the id you get a 500 internal server error.
        :return: None
        """
        self.grouped_sums_df["uid"] = self.grouped_sums_df["area"].str.replace(" ", "_") + self.cloud_acceptable_process_run_dt_str
        return None

    def drop_customers_from_zip_df(self) -> None:
        """
        Drop the 'customers' field from the zip code dataframe.
        Customer count values are not reported by all providers for zip code areas so can't calculate across all areas
        like is done in the county data.
        :return: None
        """
        self.zipcode_outage_records_df.drop(columns=["customers"], inplace=True)
        return None

    @staticmethod
    def drop_style_from_record_dfs(data_dataframe: pd.DataFrame) -> None:
        """
        Drop the 'style' field from the zip code, and county dataframes
        :return: None
        """
        drop_field = "style"
        data_dataframe.drop(columns=[drop_field], inplace=True)
        return None

    def isolate_county_style_records(self) -> None:
        """
        Isolate the county style records from the master outage dataframe
        :return: None
        """
        self.county_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.COUNTY].copy()
        return None

    def isolate_zip_style_records(self) -> None:
        """
        Isolate the zip style records from the master outage dataframe
        :return: None
        """
        self.zipcode_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.ZIP].copy()
        return None

    def group_by_area(self) -> None:
        """
        Group the master dataframe by style and area
        :return: None
        """
        self.master_groupby_area = self.master_outages_df.groupby(by=["style", "area"], axis=0, as_index=False)
        return None

    def correct_data_age_field_name(self) -> None:
        """
        Correct the field name to meet platform requirements of no space or special character
        :return: None
        """
        self.feed_status_df.rename(columns={"data age (min)": "data_age_min"}, inplace=True)
        return None

    def sum_outages(self) -> None:
        """
        Operate on the master groupby and sum the outage data for each group
        :return: None
        """
        self.grouped_sums_df = self.master_groupby_area.sum()
        return None

    @property
    def cloud_acceptable_process_run_dt_str(self) -> str:
        """
        get attribute
        :return: attribute str
        """
        return self.__cloud_acceptable_dt_string

    @cloud_acceptable_process_run_dt_str.setter
    def cloud_acceptable_process_run_dt_str(self, value: None) -> None:
        """
        Create a socrata acceptable datetime string by replacing space with 'T', to indicate time is present after date
        NOTE: Socrata at least, requires a 'T' between date and time for string to be recognized. No spaces.
        :param value: required but not used
        :return: None
        """
        self.__cloud_acceptable_dt_string = DOIT_UTIL.current_date_time_str().replace(" ", "T")


class OpenData:
    """
    Class for Socrata Open Data Platform specific functionality
    """
    RECORD_DELETION_AGE_LIMIT_DAYS = 30

    def __init__(self, parser):
        self.opendata_apptoken = parser["OPENDATA"]["APPTOKEN"]
        self.opendata_domain = parser["OPENDATA"]["DOMAIN"]
        self.password = parser["OPENDATA"]["PASSWORD"]
        self.username = parser["OPENDATA"]["USERNAME"]
        self.socrata_client = None

    def delete_records_by_uid(self, dataset_identifier: str, results_gen: types.GeneratorType) -> None:
        """
        Delete record in Socrata asset based on unique id value
        NOTE: Socrata unique id will be accepted with spaces " " but when attempt to delete based on a unique id
        with space in the id you get a 500 internal server error.
        :param dataset_identifier:
        :param results_gen:
        :return: None
        """
        for record in results_gen:
            try:
                uid = record["uid"]
            except KeyError as ke:
                print(f"KeyError with record['uid']: {record}")
                continue

            try:
                result = self.socrata_client.delete(dataset_identifier=dataset_identifier, row_id=uid)
            except req_exc.HTTPError as httperr:
                print(uid, httperr)
            else:
                print(f"\tDelete {uid}: {result}")
        return None

    def create_socrata_client(self) -> None:
        """
        Create and return a Socrata client for use.
        NOTE: It seems absolutely essential the the domain be a domain and not a url; 'https://opendata.maryland.gov'
            will not substitute for 'opendata.maryland.gov'.
        :return: Socrata connection client
        """
        self.socrata_client = Socrata(domain=self.opendata_domain, app_token=self.opendata_apptoken,
                                      username=self.username, password=self.password)
        return None

    def upsert_to_socrata(self, dataset_identifier: str, zipper: list) -> None:
        """
        Upsert data to Socrata dataset.

        :param dataset_identifier: Unique Socrata dataset identifier. Not the data page identifier but primary page id.
        :param zipper: list of dictionaries of records (headers and data values)
        :return: None
        """
        try:
            result = self.socrata_client.upsert(dataset_identifier=dataset_identifier, payload=zipper, content_type='json')
        except Exception as e:
            print("Error upserting to Socrata: {}. {}".format(dataset_identifier, e))
        else:
            print(result)
        return None

    def retrieve_old_records_for_deletion(self, dataset_identifier: str, ) -> types.GeneratorType:
        """
        Query socrata asset for all records greater than age limit of interest.
        :param dataset_identifier: four by four of the socrata asset
        :return: generator for record retrieval
        """
        historical_date_str = "{:%Y-%m-%d %H:%M:%S}".format(
            datetime.datetime.now() - datetime.timedelta(days=OpenData.RECORD_DELETION_AGE_LIMIT_DAYS)).replace(" ",
                                                                                                                "T")
        results_generator = self.socrata_client.get_all(dataset_identifier=dataset_identifier,
                                                        where=f"{VARS.date_time_field_name}<='{historical_date_str}'",
                                                        select="uid, dt_stamp",
                                                        exclude_system_fields=True)
        return results_generator


class ArcGISOnline:
    """
    Class for ArcGIS Online specific functionality
    """

    # Class Variables
    PATH_PICKER_DICT = {DOIT_UTIL.ZIP: fr"{VARS._root_project_path}/TEMP_AGOL_CSV/{DOIT_UTIL.ZIP}_temp.csv",
                        DOIT_UTIL.COUNTY: fr"{VARS._root_project_path}/TEMP_AGOL_CSV/{DOIT_UTIL.COUNTY}_temp.csv"}

    def __init__(self, parser: configparser.ConfigParser, style: str, gis_connection: arcgis.gis.GIS, data_df: pd.DataFrame):
        self.analyze_result = None
        self.csv_item = None
        self.csv_item_id = parser["ARCGIS"][f"{style}_CSV_ITEM_ID"]
        self.data_dataframe = data_df
        # self.dt_stamp_tz_aware = None
        self.hosted_table_item = None
        self.hosted_table_item_id = parser["ARCGIS"][f"{style}_HOSTED_TABLE_ITEM_ID"]
        self.features_table = None
        self.gis_connection = gis_connection
        self.style = style
        self.temp_csv_path = ArcGISOnline.PATH_PICKER_DICT.get(self.style)

    def analyze_table(self) -> None:
        """
        Esri required analysis of csv item before publishing or generating features
        :return:
        """
        self.analyze_result = self.gis_connection.content.analyze(item=self.csv_item.id)
        return None

    def append_new_outage_data(self) -> None:
        """
        Esri update of an existing hosted feature layer using append functionality
        NOTE:
            The append function periodically throws an exception, and the ESRI code is not specific and is just
            a type Exception. Was occurring 1-3 times per day out of 97 runs. Added a loop with sleep to introduce a
            small amount of wait before retrying the append. Features in existing hosted table have been deleted prior
            to the appending of new records so important to not fail out and leave an empty table in cloud.
        :return: None
        """
        attempt_ceiling = 3
        for i in range(0, attempt_ceiling):
            try:
                append_result = self.features_table.append(
                    item_id=self.csv_item.id,
                    upload_format='csv',
                    source_info=self.analyze_result,
                    upsert=False,
                )
            except Exception as e:

                # Esri exception is generic so there is no specific type to look for.
                print(f"ATTEMPT {i + 1} OF {attempt_ceiling} FAILED. Exception in ESRI arcgis.features.Table.append()\n{e}")
                time.sleep(2)
                continue
            else:
                print(f"Append Result: {append_result}")
                break
        return None

    def create_arcgis_features_table(self) -> None:
        """
        Create a feature table for the hosted data table.
        NOTE: only works when the csv is published to hosted table
        :return: None
        """
        self.features_table = arcgis.features.Table.fromitem(self.hosted_table_item)
        return None

    @staticmethod
    def create_gis_connection() -> arcgis.gis.GIS:
        """
        Create and return a connection object for ArcGIS Online
        :return: GIS connection object
        """
        return arcgis.gis.GIS(url=DOIT_UTIL.PARSER["ARCGIS"]["MD_ORG_URL"],
                              username=DOIT_UTIL.PARSER["ARCGIS"]["USERNAME"],
                              password=DOIT_UTIL.PARSER["ARCGIS"]["PASSWORD"])

    def delete_features(self) -> None:
        """
        Delete existing features in ArcGIS Online features table
        :return: None
        """
        delete_results = self.features_table.delete_features(where="1=1", return_delete_results=True)
        print(f"Delete Features: {delete_results}")
        return None

    def drop_unnecessary_fields(self) -> None:
        """
        Drop fields from source dataframe that are not needed for arcgis online
        :return: None
        """
        self.data_dataframe.drop(columns=["uid",], inplace=True)
        return None

    def get_arcgis_item(self, item_id: str) -> arcgis.gis.Item:
        """
        Get an arcgis online Item using the item id.
        :param item_id: unique id for the item
        :return: Item object
        """
        return self.gis_connection.content.get(itemid=item_id)

    def localize_dt_values(self) -> None:
        """
        Convert a naive datetime value to a timezone aware value
        Note: Because all dt_stamp values are identical value, don't need to apply inner function to each row,
            just need to broadcast adjusted value
        :return: None
        """
        try:

            # safeguard against rare scenario where there are zero outage records in dataframe
            dt_naive_value = self.data_dataframe.iloc[0][VARS.date_time_field_name]
        except IndexError as ie:
            print(ie)
            print(f"{self.style} data_dataframe size: {self.data_dataframe.size}")
        else:
            dt_naive_string = datetime.datetime.strptime(dt_naive_value, VARS.datetime_format_str_naive)
            dt_aware_value = VARS.eastern_tz.localize(dt_naive_string)
            self.data_dataframe[VARS.date_time_field_name] = dt_aware_value.strftime(VARS.datetime_format_str_aware)
        return None

    def update_csv_item(self) -> None:
        """
        Esri update item using csv, a path is required.
        :return: None
        """
        update_result = self.csv_item.update(data=self.temp_csv_path)
        print(f"Update CSV Item Result: {update_result}")
        return None

    def write_temp_csv(self) -> None:
        """
        Write outage dataframe to csv so that have a path to provide the update function for arcgis online.
        :return:
        """
        self.data_dataframe.to_csv(path_or_buf=self.temp_csv_path, index=False)
        return None





