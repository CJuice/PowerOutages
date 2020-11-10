"""

"""

import pandas as pd
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import dataclasses
from sodapy import Socrata

class CloudStorage:
    """

    """

    def __init__(self, parser):
        self.socrata_dt_string = None
        self.master_outages_df = None
        self.feed_status_df = None
        self.outages_as_record_dicts_list = []
        self.zipcode_outage_records_df = None
        self.county_outage_records_df = None
        self.master_groupby_area = None
        self.grouped_sums_df = None
        self.zipcode_zipper = None
        self.county_zipper = None
        self.feed_status_zipper = None
        self.socrata_client = None
        self.opendata_apptoken = parser["OPENDATA"]["APPTOKEN"]
        self.opendata_domain = parser["OPENDATA"]["DOMAIN"]
        self.opendata_password = parser["OPENDATA"]["PASSWORD"]
        self.opendata_username = parser["OPENDATA"]["USERNAME"]

    def create_socrata_acceptable_dt_string(self):
        """TODO
        NOTE: Socrata requires a 'T' between date and time for string to be recognized. No spaces.
        """
        self.socrata_dt_string = DOIT_UTIL.current_date_time().replace(" ", "T")

    def isolate_zip_style_records(self):
        """TODO"""
        self.zipcode_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.ZIP]

    def isolate_county_style_records(self):
        """TODO"""
        self.county_outage_records_df = self.grouped_sums_df[self.grouped_sums_df["style"] == DOIT_UTIL.COUNTY]

    def group_by_area(self):
        """TODO"""
        self.master_groupby_area = self.master_outages_df.groupby(by=["style", "area"], axis=0, as_index=False)

    def sum_outages(self):
        """TODO"""
        self.grouped_sums_df = self.master_groupby_area.sum()

    def create_unique_id_outages(self):
        """TODO"""
        self.grouped_sums_df["uid"] = self.grouped_sums_df["area"] + self.socrata_dt_string

    def create_unique_id_feed_status(self):
        """TODO"""
        self.feed_status_df["uid"] = self.feed_status_df["prov_style"] + self.socrata_dt_string

    def create_dt_stamp_column(self):
        """TODO"""
        self.grouped_sums_df["dt_stamp"] = self.socrata_dt_string

    def calculate_county_outage_percentage(self):
        """TODO"""
        # SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame.
        #   Try using .loc[row_indexer,col_indexer] = value instead. Still throws a SettingWithCopyWarning
        with pd.option_context('mode.chained_assignment', None):
            print(pd.options.mode.chained_assignment)
            print("NOTE: Pandas mode.chained_assignment set to None to handle SettingWithCopyWarning in calculate_county_outage_percentage")
            self.county_outage_records_df["percent_out"] = self.county_outage_records_df.loc[:, "outages"].copy() / self.county_outage_records_df.loc[:, "customers"].copy() * 100
            # self.county_outage_records_df["percent_out"] = self.county_outage_records_df.apply(func=lambda row: row["outages"] / row["customers"] * 100, axis=1, raw=False, result_type=None)

    def create_outage_records(self, provider_objects: dict):
        """TODO"""
        for key, obj in provider_objects.items():
            self.outages_as_record_dicts_list.extend([dataclasses.asdict(stat_obj) for stat_obj in obj.stats_objects])

    def create_master_outage_dataframe(self):
        """TODO"""
        self.master_outages_df = pd.DataFrame.from_records(data=self.outages_as_record_dicts_list,
                                                           columns=["style", "area", "outages", "customers"])

    def create_feed_status_dataframe(self, status_check_output: dict):
        """TODO
        """
        self.feed_status_df = pd.DataFrame(data=status_check_output).transpose().reset_index().rename(columns={"index": "prov_style"})

    def correct_status_created_dt(self):
        """
        TODO
        :return:
        """
        self.feed_status_df["created"] = self.feed_status_df["created"].apply(lambda x: x.replace(" ", "T"))

    def drop_customers_from_zip_df(self):
        """TODO"""
        self.zipcode_outage_records_df.drop(columns=["customers"], inplace=True)

    def drop_style_from_record_dfs(self):
        """TODO"""
        drop_field = "style"
        self.zipcode_outage_records_df.drop(columns=[drop_field], inplace=True)
        self.county_outage_records_df.drop(columns=[drop_field], inplace=True)

    def create_lists_of_record_dicts(self):
        """

        :return:
        """
        self.county_zipper = self.county_outage_records_df.to_dict(orient="records")
        self.zipcode_zipper = self.zipcode_outage_records_df.to_dict(orient="records")
        self.feed_status_zipper = self.feed_status_df.to_dict(orient="records")

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