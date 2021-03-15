"""
Class file for cloud storage of outage related data.
Contains variables and functionality for processing and upserting data to our Socrata open data portal
TODO: Create OpenDataPortal and ArcGisOnline subclasses that inherit from CloudStorage
"""

from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS

from sodapy import Socrata
import arcgis
# from arcgis.features import Table
import dataclasses
import pandas as pd
from datetime import datetime
# from pytz import timezone
import configparser


class CloudStorage:
    """
    Variables and functionality for processing and cloud interactions of outage data.
    """

    def __init__(self, parser):
        self.county_outage_records_df = None
        self.county_zipper = None
        self.feed_status_df = None
        self.feed_status_zipper = None
        self.grouped_sums_df = None
        self.master_groupby_area = None
        self.master_outages_df = None
        # self.opendata_apptoken = parser["OPENDATA"]["APPTOKEN"]
        # self.opendata_domain = parser["OPENDATA"]["DOMAIN"]
        # self.password = None
        # self.username = None
        self.outages_as_record_dicts_list = []
        self.cloud_acceptable_dt_string = None
        self.zipcode_outage_records_df = None
        self.zipcode_zipper = None

    def calculate_county_outage_percentage(self) -> None:
        """
        Calculate the outage percentage for each county using the outage counts and customer counts, multiplied by 100

        Note: Encountered classic "SettingWithCopyWarning: A value is trying to be set on a copy of a slice from
        a DataFrame. Try using .loc[row_indexer,col_indexer] = value instead." Revised functionality but still
        throws a SettingWithCopyWarning. Tried multiple ways but did not succeed so used context manager to change
        mode > chained assignment.
        :return: None
        """
        with pd.option_context('mode.chained_assignment', None):
            print(pd.options.mode.chained_assignment)
            print("NOTE: Pandas mode.chained_assignment set to None to handle SettingWithCopyWarning in calculate_county_outage_percentage")
            self.county_outage_records_df["percent_out"] = self.county_outage_records_df.loc[:, "outages"].copy() / self.county_outage_records_df.loc[:, "customers"].copy() * 100
            # self.county_outage_records_df["percent_out"] = self.county_outage_records_df.apply(func=lambda row: row["outages"] / row["customers"] * 100, axis=1, raw=False, result_type=None)
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
        dataframe[VARS.date_time_field_name] = self.cloud_acceptable_dt_string
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
    def create_lists_of_record_dicts(data_dataframe: pd.DataFrame) -> list:
        """
        Create list of record data from record dataframes.
        For upsert payload to socrata open data portal.
        :param data_dataframe: pandas dataframe
        :return: list of dict records
        """
        return data_dataframe.to_dict(orient="records")

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

    def create_cloud_acceptable_dt_string(self) -> None:
        """
        Create a socrata acceptable datetime string by replacing space with 'T' to indicate time is present
        NOTE: Socrata at least, requires a 'T' between date and time for string to be recognized. No spaces.
        :return: None
        """
        self.cloud_acceptable_dt_string = DOIT_UTIL.current_date_time().replace(" ", "T")
        return None

    def create_unique_id_feed_status(self) -> None:
        """
        Combine provider style key with socrata acceptable datetime string to make a record unique id for feed status
        :return: None
        """
        self.feed_status_df["uid"] = self.feed_status_df["prov_style"] + self.cloud_acceptable_dt_string
        return None

    def create_unique_id_outages(self) -> None:
        """
        Combine area value with socrata acceptable datetime string to make a record unique id for group sums
        # TODO: If move to tz aware this unique_id will change, would need to revise existing data
        :return:
        """
        self.grouped_sums_df["uid"] = self.grouped_sums_df["area"] + self.cloud_acceptable_dt_string

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
        self.county_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.COUNTY]
        return None

    def isolate_zip_style_records(self) -> None:
        """
        Isolate the zip style records from the master outage dataframe
        :return: None
        """
        self.zipcode_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.ZIP]
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
        TODO
        :return:
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


class OpenData:
    """
    TODO
    """
    def __init__(self, parser):
        # super(CloudStorage, self).__init__(parser=parser)
        self.opendata_apptoken = parser["OPENDATA"]["APPTOKEN"]
        self.opendata_domain = parser["OPENDATA"]["DOMAIN"]
        self.password = parser["OPENDATA"]["PASSWORD"]
        self.username = parser["OPENDATA"]["USERNAME"]
        self.socrata_client = None

    def create_socrata_client(self) -> None:
        """
        Create and return a Socrata client for use.

        NOTE_1: It seems absolutely essential the the domain be a domain and not a url; 'https://opendata.maryland.gov'
            will not substitute for 'opendata.maryland.gov'.

        :param maryland_domain: domain for maryland open data portal.
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
        return


class ArcGISOnline:
    """
    TODO
    """

    PATH_PICKER_DICT = {DOIT_UTIL.ZIP: f"./TEMP_AGOL_CSV/{DOIT_UTIL.ZIP}_temp.csv",
                        DOIT_UTIL.COUNTY: f"./TEMP_AGOL_CSV/{DOIT_UTIL.COUNTY}_temp.csv"}

    def __init__(self, parser: configparser.ConfigParser, style: str, gis_connection: arcgis.gis.GIS, data_df: pd.DataFrame):
        self.analyze_result = None
        self.csv_item = None
        self.csv_item_id = parser["ARCGIS"][f"{style}_CSV_ITEM_ID"]
        self.data_dataframe = data_df
        self.hosted_table_item = None
        self.hosted_table_item_id = parser["ARCGIS"][f"{style}_HOSTED_TABLE_ITEM_ID"]
        self.features_table = None
        self.gis_connection = gis_connection
        self.style = style
        self.temp_csv_path = ArcGISOnline.PATH_PICKER_DICT.get(self.style)

    def analyze_table(self) -> None:
        """
        TODO
        :return:
        """
        self.analyze_result = self.gis_connection.content.analyze(item=self.csv_item.id)

    def append_new_outage_data(self) -> None:
        """
        TODO
        :return:
        """
        append_result = self.features_table.append(
            item_id=self.csv_item.id,
            upload_format='csv',
            source_info=self.analyze_result,
            upsert=False,
        )
        print(f"Append Result: {append_result}")
        return None

    @staticmethod
    def create_gis_connection() -> arcgis.gis.GIS:
        """
        TODO
        :return:
        """
        return arcgis.gis.GIS(url=DOIT_UTIL.PARSER["ARCGIS"]["MD_ORG_URL"],
                              username=DOIT_UTIL.PARSER["ARCGIS"]["USERNAME"],
                              password=DOIT_UTIL.PARSER["ARCGIS"]["PASSWORD"])

    def delete_features(self) -> None:
        """
        TODO
        :param self:
        :return:
        """
        delete_results = self.features_table.delete_features(where="1=1", return_delete_results=True)
        print(f"Delete Features: {delete_results}")
        return None

    def drop_unnecessary_fields(self):
        """
        TODO
        :return:
        """
        self.data_dataframe.drop(columns=["uid",], inplace=True)

    def get_arcgis_item(self, item_id: str) -> arcgis.gis.Item:
        """
        TODO
        :param item_id:
        :return:
        """
        return self.gis_connection.content.get(itemid=item_id)

    def create_arcgis_features_table(self):
        """
        TODO
        # only works when the csv is published to hosted table
        :return:
        """
        self.features_table = arcgis.features.Table.fromitem(self.hosted_table_item)

    def localize_dt_values(self) -> None:
        """
        TODO
        :return:
        """
        def inner_localize_func(dt_str: str):
            """
            TODO
            Note: For performance improvement, placed creation of eastern tz object in centralized variables so only
            instantiate once. Instantiation seemed costly.
            :param dt_str:
            :return:
            """
            # TODO: Assess if there is a way to set the tz on datetime instead of using localize
            dt_value = datetime.strptime(dt_str, VARS.datetime_format_str_naive)
            loc_dt = VARS.eastern_tz.localize(dt_value)
            return loc_dt.strftime(VARS.datetime_format_str_aware)

        # FIXME: SettingWithCopyWarning on this dt adjustment
        self.data_dataframe[VARS.date_time_field_name] = self.data_dataframe[VARS.date_time_field_name].apply(inner_localize_func)
        return None

    def update_csv_item(self):
        """
        TODO
        :return:
        """
        update_result = self.csv_item.update(data=self.temp_csv_path)
        print(f"Update CSV Item Result: {update_result}")
        return None

    def write_temp_csv(self) -> None:
        """
        TODO: Need to write zipcode and also county data to temp csv so that can upload to arcgis online.
        :return:
        """
        self.data_dataframe.to_csv(path_or_buf=self.temp_csv_path, index=False)
        return None





