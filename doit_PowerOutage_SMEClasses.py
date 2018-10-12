"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage


class SME(Provider):
    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.area = None
        self.outage_events_list = None
        self.desc_list = None
        self.stats_objects = None

    def extract_outage_events_list(self, data_json):
        self.outage_events_list = doit_util.extract_attribute_from_dict(data_dict=data_json, attribute_name="file_data")

    def extract_outage_counts_by_desc(self):
        list_of_stats_objects = []
        for obj in self.outage_events_list:
            desc_dict = doit_util.extract_attribute_from_dict(data_dict=obj, attribute_name="desc")
            area = doit_util.extract_attribute_from_dict(data_dict=obj, attribute_name="id")
            cust_affected_dict = doit_util.extract_attribute_from_dict(data_dict=desc_dict, attribute_name="cust_a")
            outages = doit_util.extract_attribute_from_dict(data_dict=cust_affected_dict, attribute_name="val")
            customers = doit_util.extract_attribute_from_dict(data_dict=desc_dict, attribute_name="cust_s")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=area,
                                                outages=outages,
                                                customers=customers,
                                                state="none given"))
        self.stats_objects = list_of_stats_objects
        return
