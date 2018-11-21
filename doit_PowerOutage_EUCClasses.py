"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import json


class EUC(Provider):

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.events_list = None
        self.zip_to_county = {"21601": "Talbot"}

    def extract_outage_events_list_from_xml_str(self):
        content_list_as_str = self.xml_element.text
        self.events_list = json.loads(content_list_as_str)
        return

    def extract_outage_counts(self):
        list_of_stats_objects = []
        for event in self.events_list:
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=event, attribute_name="Count")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=event, attribute_name="AccountCount")
            area = DOIT_UTIL.extract_attribute_from_dict(data_dict=event, attribute_name="ZipCode")

            # At time of original design, EUC only served zip 21601 and did not provide county name (Talbot) in feed.
            if self.style == DOIT_UTIL.COUNTY and area in self.zip_to_county.keys():
                area = self.zip_to_county[area]
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=area,
                                                outages=outages,
                                                customers=customers,
                                                state=DOIT_UTIL.MARYLAND)
                                         )
        self.stats_objects = list_of_stats_objects
        return

    def extract_date_created(self):
        for event in self.events_list:
            self.date_created = DOIT_UTIL.extract_attribute_from_dict(data_dict=event, attribute_name="TimeStamp")
        return