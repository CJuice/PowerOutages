"""
Module contains a EUC class that inherits from Provider class. EUC class is an implementation specific to the
peculiarities of the EUC feeds and the processing they require that is not common to all providers.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
import json


class EUC(Provider):
    """
    EUC specific functionality and variables for handling EUC feed data. Inherits from Provider.
    EUC is unique in that the provider only serves a single zip code, at time of Version 2 build, and does not provide
    feed data by county.
    """

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.events_list = None
        self.zip_to_county = {"21601": "Talbot"}

    def extract_date_created(self) -> None:
        """
        Extract the date created from the events list.
        :return: None
        """
        for event in self.events_list:
            self.date_created = DOIT_UTIL.extract_attribute_from_dict(data_dict=event, attribute_name="TimeStamp")
        return

    def extract_outage_counts(self) -> None:
        """
        Extract outage counts, customer counts, and area from events list, exchange zip for county, then
        build stat objects.
        :return: None
        """
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

    def extract_outage_events_list_from_xml_str(self) -> None:
        """
        Extract outage events from xml response
        :return: None
        """
        content_list_as_str = self.xml_element.text
        self.events_list = json.loads(content_list_as_str)
        return
