"""
Class file for cloud storage of outage related data.
Contains variables and functionality for processing and upserting data to our Socrata open data portal
TODO: Create OpenDataPortal and ArcGisOnline subclasses that inherit from CloudStorage
"""

from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from sodapy import Socrata
# import arcgis
import dataclasses
import pandas as pd


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
        self.opendata_apptoken = parser["OPENDATA"]["APPTOKEN"]
        self.opendata_domain = parser["OPENDATA"]["DOMAIN"]
        self.opendata_password = parser["OPENDATA"]["PASSWORD"]
        self.opendata_username = parser["OPENDATA"]["USERNAME"]
        self.outages_as_record_dicts_list = []
        self.socrata_client = None
        self.socrata_dt_string = None
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
        dataframe["dt_stamp"] = self.socrata_dt_string
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

    def create_lists_of_record_dicts(self) -> None:
        """
        Create list of record data from record dataframes for upsert payload to socrata open data portal.
        Performs the action on the county, zipcode, and feed status dataframes in one call.
        :return: None
        """
        self.county_zipper = self.county_outage_records_df.to_dict(orient="records")
        self.zipcode_zipper = self.zipcode_outage_records_df.to_dict(orient="records")
        self.feed_status_zipper = self.feed_status_df.to_dict(orient="records")
        return None

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

    def create_socrata_acceptable_dt_string(self) -> None:
        """
        Create a socrata acceptable datetime string by replacing space with 'T'
        NOTE: Socrata requires a 'T' between date and time for string to be recognized. No spaces.
        :return: None
        """
        #TODO: incorporate utc offset so tz aware, use '%Y-%m-%dT%H:%M:%S%z'. AGOL recognizes as valid also.
        #   Socrata field type as floating or fixed? How will the type affect downstream apps
        #   MEMA sql db may not like new format! Check first or use separate cloud format and a mema db format
        self.socrata_dt_string = DOIT_UTIL.current_date_time(tz_aware=False).replace(" ", "T")
        return None

    def create_socrata_client(self) -> None:
        """
        Create and return a Socrata client for use.

        NOTE_1: It seems absolutely essential the the domain be a domain and not a url; 'https://opendata.maryland.gov'
            will not substitute for 'opendata.maryland.gov'.

        :param maryland_domain: domain for maryland open data portal.
        :return: Socrata connection client
        """
        self.socrata_client = Socrata(domain=self.opendata_domain, app_token=self.opendata_apptoken,
                                      username=self.opendata_username, password=self.opendata_password)
        return None

    def create_unique_id_feed_status(self) -> None:
        """
        Combine provider style key with socrata acceptable datetime string to make a record unique id for feed status
        :return: None
        """
        self.feed_status_df["uid"] = self.feed_status_df["prov_style"] + self.socrata_dt_string
        return None

    def create_unique_id_outages(self) -> None:
        """
        Combine area value with socrata acceptable datetime string to make a record unique id for group sums

        :return:
        """
        self.grouped_sums_df["uid"] = self.grouped_sums_df["area"] + self.socrata_dt_string

    def drop_customers_from_zip_df(self) -> None:
        """
        Drop the 'customers' field from the zip code dataframe.
        Customer count values are not reported by all providers for zip code areas so can't calculate across all areas
        like is done in the county data.
        :return: None
        """
        self.zipcode_outage_records_df.drop(columns=["customers"], inplace=True)
        return None

    def drop_style_from_record_dfs(self) -> None:
        """
        Drop the 'style' field from the zip code, and county dataframes
        :return: None
        """
        drop_field = "style"
        self.zipcode_outage_records_df.drop(columns=[drop_field], inplace=True)
        self.county_outage_records_df.drop(columns=[drop_field], inplace=True)
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

    def sum_outages(self) -> None:
        """
        Operate on the master groupby and sum the outage data for each group
        :return: None
        """
        self.grouped_sums_df = self.master_groupby_area.sum()
        return None

    def upsert_to_socrata(self, dataset_identifier: str, zipper: dict) -> None:
        """
        Upsert data to Socrata dataset.

        :param dataset_identifier: Unique Socrata dataset identifier. Not the data page identifier but primary page id.
        :param zipper: dictionary of zipped results (headers and data values)
        :return: None
        """
        try:
            self.socrata_client.upsert(dataset_identifier=dataset_identifier, payload=zipper, content_type='json')
        except Exception as e:
            print("Error upserting to Socrata: {}. {}".format(dataset_identifier, e))
        return


class OpenData(CloudStorage):
    """

    """
    def __init__(self, parser):
        super(CloudStorage, self).__init__(parser=parser)


class ArcGISOnline(CloudStorage):
    """

    """
    def __init__(self, parser):
        super(CloudStorage, self).__init__(parser=parser)