"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
import json


class CTK(Provider):
    # TODO: REfactor to use doit_util.extract_features_from_element()
    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.outage_report = None
        self.outage_dataset = None

    def extract_date_created(self):
        date_generated = doit_util.extract_first_immediate_child_feature_from_element(element=self.xml_element, tag_name="generated")
        date_dict = date_generated.attrib
        self.date_created = doit_util.extract_attribute_from_dict(data_dict=date_dict, attribute_name="date")
        return

    def extract_report_by_id(self, id):
        for report in self.xml_element.iter("report"):
            if report.attrib["id"].lower() == id.lower():
                self.outage_report = report
                return

    def extract_outage_dataset(self):
        self.outage_dataset = self.outage_report.find("dataset")
        if len(self.outage_dataset) == 0:
            print(f"No {self.abbrev}_{self.style} dataset values in feed.")
        return

    def extract_outage_counts_from_dataset(self):
        list_of_stats_objects = []
        t_elements = self.outage_dataset.findall("t")
        area_index, customers_index, affected_index = (0, 1, 2)
        for t in t_elements:
            e_list = t.findall("e")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=e_list[area_index].text,
                                                outages=e_list[affected_index].text,
                                                customers=e_list[customers_index].text,
                                                state="MD"))
        self.stats_objects = list_of_stats_objects
        return
