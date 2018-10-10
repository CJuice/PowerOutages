"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider


class FES(Provider):
    def __init__(self, provider_abbrev):
        super().__init__(provider_abbrev=provider_abbrev)
        self.md_area_dict = None
        # self.xml_dom = None
        # self.xml_metadata_element = None

    def extract_maryland_area_dict_from_county_response(self):
        dict_as_json = self.data_feed_response.json()
        areas_list = dict_as_json["file_data"]["curr_custs_aff"]["areas"]
        for area in areas_list:
            if area["area_name"] == "MD":
                self.md_area_dict = area
                return
