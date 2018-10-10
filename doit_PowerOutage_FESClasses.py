"""

"""
from dataclasses import dataclass
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
import pprint
pp = pprint.PrettyPrinter(indent=4)


class FES(Provider):
    COUNTY_DB_UPDATE_STATEMENT = """exec RealTime_UpdatePowerOutagesCounty {outage}, '{county}', 'FES', 'Maryland'"""
    ZIP_DB_UPDATE_STATEMENT = """exec RealTime_UpdatePowerOutagesZip {outage}, '{zip_code}', 'FES'"""

    def __init__(self, provider_abbrev):
        super().__init__(provider_abbrev=provider_abbrev)
        self.md_area_dict = None
        self.zip_events_list = None
        self.stats_objects_by_county = None
        self.stats_objects_by_zip = None

    def extract_maryland_dict_from_county_response(self):
        dict_as_json = self.data_feed_response.json()
        areas_list = dict_as_json["file_data"]["curr_custs_aff"]["areas"]
        for area in areas_list:
            if area["area_name"] == "MD":
                self.md_area_dict = area
                return

    def extract_outage_counts_by_county(self):
        @dataclass
        class CountyOutage:
            county: str
            outages: int
            customers: int

        counties_list = self.md_area_dict["areas"]
        stats_objects_by_county = []
        for county_dict in counties_list:
            county = county_dict["area_name"]
            outages = int(county_dict["custs_out"])
            customers = int(county_dict["total_custs"])
            stats_objects_by_county.append(CountyOutage(county=county,
                                                        outages=outages,
                                                        customers=customers))
        self.stats_objects_by_county = stats_objects_by_county
        return

    def change_county_name_case_to_title(self):
        for obj in self.stats_objects_by_county:
            obj.county = obj.county.title()

    def extract_events_from_zip_response(self):
        dict_as_json = self.data_feed_response.json()
        self.zip_events_list = dict_as_json["file_data"]

    def extract_outage_counts_by_zip(self):
        @dataclass
        class ZIPOutage:
            zip_: str
            outages: int
            customers: int

        stats_objects_by_zip = []
        for area in self.zip_events_list:

            # Expecting list (len=1) of dicts. Guarding against greater length via *rest
            description, *rest = area["desc"]
            zip_code = area["id"]
            outages = description["cust_a"]
            customers = description["cust_s"]
            stats_objects_by_zip.append(ZIPOutage(zip_=zip_code, outages=outages, customers=customers))

        self.stats_objects_by_zip = stats_objects_by_zip
        return

    def remove_commas_from_counts(self):
        for obj in self.stats_objects_by_zip:
            obj.outages = obj.outages.replace(",", "")
            obj.customers = obj.customers.replace(",", "")
        return

    def process_outage_counts_to_integers(self):
        replacement_values_dict = {"Less than 5": 1, "<5": 1}
        for obj in self.stats_objects_by_zip:
            try:
                obj.outages = int(obj.outages)
            except ValueError as ve:
                try:
                    obj.outages = replacement_values_dict[obj.outages]
                except KeyError as ke:
                    obj.outages = -9999
        return

    def process_customer_counts_to_integers(self):
        for obj in self.stats_objects_by_zip:
            try:
                obj.customers = int(obj.customers)
            except ValueError as ve:
                obj.customers = -9999
        return
