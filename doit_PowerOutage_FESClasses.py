"""

"""
from dataclasses import dataclass
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage

import pprint
pp = pprint.PrettyPrinter(indent=4)


class FES(Provider):

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.md_area_dict = None
        self.zip_events_list = None
        self.stats_objects_by_county = None
        self.stats_objects_by_zip = None

    def extract_maryland_dict_from_county_response(self):
        dict_as_json = self.data_feed_response.json()
        file_data = doit_util.extract_attribute_from_dict(data_dict=dict_as_json, attribute_name="file_data")
        curr_custs_aff = doit_util.extract_attribute_from_dict(data_dict=file_data, attribute_name="curr_custs_aff")
        areas_list = doit_util.extract_attribute_from_dict(data_dict=curr_custs_aff, attribute_name="areas")
        # areas_list = dict_as_json["file_data"]["curr_custs_aff"]["areas"]
        for area in areas_list:
            if area["area_name"] == "MD":
                self.md_area_dict = area
                return

    def extract_outage_counts_by_county(self):
        counties_list = doit_util.extract_attribute_from_dict(data_dict=self.md_area_dict, attribute_name="areas")
        list_of_stats_objects_by_county = []
        for county_dict in counties_list:
            county = doit_util.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
            outages = doit_util.extract_attribute_from_dict(data_dict=county_dict, attribute_name="custs_out")
            customers = doit_util.extract_attribute_from_dict(data_dict=county_dict, attribute_name="total_custs")
            list_of_stats_objects_by_county.append(Outage(abbrev=self.abbrev,
                                                          style=self.style,
                                                          area=county,
                                                          outages=outages,
                                                          customers=customers,
                                                          state="MD"))
        self.stats_objects_by_county = list_of_stats_objects_by_county
        return

    def extract_events_from_zip_response(self):
        dict_as_json = self.data_feed_response.json()
        self.zip_events_list = doit_util.extract_attribute_from_dict(data_dict=dict_as_json, attribute_name="file_data")

    def extract_outage_counts_by_zip(self):
        stats_objects_by_zip = []
        for area in self.zip_events_list:

            # Expecting list (len=1) of dicts. Guarding against greater length via *rest
            description, *rest = doit_util.extract_attribute_from_dict(data_dict=area, attribute_name="desc")
            zip_code = doit_util.extract_attribute_from_dict(data_dict=area, attribute_name="id")
            outages = doit_util.extract_attribute_from_dict(data_dict=description, attribute_name="cust_a")
            customers = doit_util.extract_attribute_from_dict(data_dict=description, attribute_name="cust_s")
            stats_objects_by_zip.append(Outage(abbrev=self.abbrev,
                                               style=self.style,
                                               area=zip_code,
                                               outages=outages,
                                               customers=customers,
                                               state="none given"))

        self.stats_objects_by_zip = stats_objects_by_zip
        return

    # def remove_commas_from_counts(self):
    #     for obj in self.stats_objects_by_zip:
    #         obj.outages = obj.outages.replace(",", "")
    #         obj.customers = obj.customers.replace(",", "")
    #     return
    #
    # def process_outage_counts_to_integers(self):
    #     replacement_values_dict = {"Less than 5": 1, "<5": 1}
    #     for obj in self.stats_objects_by_zip:
    #         try:
    #             obj.outages = int(obj.outages)
    #         except ValueError as ve:
    #             try:
    #                 obj.outages = replacement_values_dict[obj.outages]
    #             except KeyError as ke:
    #                 obj.outages = -9999
    #     return

    def process_customer_counts_to_integers(self):
        for obj in self.stats_objects_by_zip:
            try:
                obj.customers = int(obj.customers)
            except ValueError as ve:
                obj.customers = -9999
        return
