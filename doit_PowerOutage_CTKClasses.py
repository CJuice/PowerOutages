"""
Module contains a CTK class that inherits from Provider class. CTK class is an implementation specific to the
peculiarities of the CTK feeds and the processing they require that is not common to all providers.
"""
from doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from doit_PowerOutage_ProviderClasses import Outage
from doit_PowerOutage_ProviderClasses import Provider


class CTK(Provider):
    """
    CTK specific functionality and variables for handling CTK feed data. Inherits from Provider.
    CTK has unique requirements related to zip codes. CTK accesses a table called RealTime_PowerOutagesZipcodes_Grouped.
    The table contains strings that are grouped zip code values separated by commas. Thesa are used during the insertion
    of counts data into RealTime_PowerOutagesZipcodes.
    """

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.outage_report = None
        self.outage_dataset = None
        self.grouped_zipcodes_dict = None

    def extract_date_created(self):
        """
        Extract the date created from the xml response content
        :return: none
        """
        date_generated = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=self.xml_element,
                                                                                      tag_name="generated")
        date_dict = date_generated.attrib
        self.date_created = DOIT_UTIL.extract_attribute_from_dict(data_dict=date_dict, attribute_name="date")
        return

    def extract_outage_counts_from_dataset(self):
        """
        Extract the outage counts from the outage dataset xml and build stat objects to store the data.
        :return: none
        """
        list_of_stats_objects = []
        t_elements = DOIT_UTIL.extract_all_immediate_child_features_from_element(element=self.outage_dataset,
                                                                                 tag_name="t")
        area_index, customers_index, affected_index = (0, 1, 2)
        for t in t_elements:
            e_list = DOIT_UTIL.extract_all_immediate_child_features_from_element(element=t, tag_name="e")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=e_list[area_index].text,
                                                outages=e_list[affected_index].text,
                                                customers=e_list[customers_index].text,
                                                state=DOIT_UTIL.MARYLAND))
        self.stats_objects = list_of_stats_objects
        return

    def extract_outage_dataset(self):
        """
        Extract the outage dataset from xml.
        :return: none
        """
        self.outage_dataset = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=self.outage_report,
                                                                                           tag_name="dataset")
        if len(self.outage_dataset) == 0:
            print(f"No {self.abbrev}_{self.style} dataset values in feed.\n\tResponse value: {self.data_feed_response}")
        return

    def extract_report_by_id(self):
        """
        Extract the data report based on id.
        :return:
        """
        style_id = self.style
        for report in self.xml_element.iter("report"):
            if report.attrib["id"].lower() == style_id.lower():
                self.outage_report = report
                return
