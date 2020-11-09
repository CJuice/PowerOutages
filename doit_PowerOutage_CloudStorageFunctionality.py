"""

"""

import pandas as pd
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import dataclasses
import pandas as pd

class CloudStorage:
    """

    """

    def __init__(self):
        self.socrata_dt_string = None
        self.master_outages_df = None
        self.outages_as_record_dicts_list = []
        self.zipcode_outage_records_df = None
        # self.zipcode_outage_records_nocust_df = None
        self.county_outage_records_df = None
        self.master_groupby_area = None
        self.grouped_sums_df = None
        self.zipcode_zipper = None
        self.county_zipper = None

    def create_socrata_acceptable_dt_string(self):
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
        # self.zipcode_outage_records_df.sum()
        # self.county_outage_records_df.sum()

    def create_unique_id(self):
        """TODO"""
        self.grouped_sums_df["uid"] = self.grouped_sums_df["area"] + self.socrata_dt_string

    def create_dt_stamp_column(self):
        """TODO"""
        self.grouped_sums_df["dt_stamp"] = self.socrata_dt_string

    def calculate_county_outage_percentage(self):
        """TODO"""
        # FIXME: SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame. Try using .loc[row_indexer,col_indexer] = value instead
        county_copy = self.county_outage_records_df.copy()
        self.county_outage_records_df["percent_out"] = county_copy["outages"] / county_copy["customers"] * 100

    def create_outage_records(self, provider_objects: dict):
        """TODO"""
        for key, obj in provider_objects.items():
            self.outages_as_record_dicts_list.extend([dataclasses.asdict(stat_obj) for stat_obj in obj.stats_objects])

    def create_master_outage_dataframe(self):
        """TODO"""
        self.master_outages_df = pd.DataFrame.from_records(data=self.outages_as_record_dicts_list,
                                                           columns=["style", "area", "outages", "customers"])

    def drop_customers_from_zip_df(self):
        """TODO"""
        self.zipcode_outage_records_df.drop(columns=["customers"], inplace=True)

    def drop_style_from_record_dfs(self):
        """TODO"""
        field = "style"
        self.zipcode_outage_records_df.drop(columns=[field], inplace=True)
        self.county_outage_records_df.drop(columns=[field], inplace=True)

    def create_lists_of_record_dicts(self):
        """"""
        self.county_zipper = self.county_outage_records_df.to_dict(orient="records")
        self.zipcode_zipper = self.zipcode_outage_records_df.to_dict(orient="records")
