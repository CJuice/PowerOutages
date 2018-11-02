"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL


class FES(Provider):

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.md_area_dict = None
        self.zip_events_list = None

    def extract_maryland_dict_from_county_response(self):
        dict_as_json = self.data_feed_response.json()
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=dict_as_json, attribute_name="file_data")
        curr_custs_aff = DOIT_UTIL.extract_attribute_from_dict(data_dict=file_data, attribute_name="curr_custs_aff")
        areas_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=curr_custs_aff, attribute_name="areas")
        for area in areas_list:
            if area["area_name"] == "MD":
                self.md_area_dict = area
                return

    def extract_outage_counts_by_county(self):
        counties_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=self.md_area_dict, attribute_name="areas")
        list_of_stats_objects_by_county = []
        for county_dict in counties_list:
            county = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="custs_out")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="total_custs")
            list_of_stats_objects_by_county.append(Outage(abbrev=self.abbrev,
                                                          style=self.style,
                                                          area=county,
                                                          outages=outages,
                                                          customers=customers,
                                                          state=self.maryland))
        self.stats_objects = list_of_stats_objects_by_county
        return

    def extract_events_from_zip_response(self):
        dict_as_json = self.data_feed_response.json()
        self.zip_events_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=dict_as_json, attribute_name="file_data")
        return

    def extract_outage_counts_by_zip(self):
        stats_objects_by_zip = []
        for area in self.zip_events_list:
            # Expecting list (len=1) of dicts. Guarding against greater length via *rest
            description, *rest = DOIT_UTIL.extract_attribute_from_dict(data_dict=area, attribute_name="desc")
            zip_code = DOIT_UTIL.extract_attribute_from_dict(data_dict=area, attribute_name="id")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=description, attribute_name="cust_a")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=description, attribute_name="cust_s")
            stats_objects_by_zip.append(Outage(abbrev=self.abbrev,
                                               style=self.style,
                                               area=zip_code,
                                               outages=outages,
                                               customers=customers,
                                               state=self.maryland))
        self.stats_objects = stats_objects_by_zip
        return

    def process_customer_counts_to_integers(self):
        for obj in self.stats_objects:
            try:
                obj.customers = int(obj.customers)
            except ValueError as ve:
                obj.customers = -9999
        return
