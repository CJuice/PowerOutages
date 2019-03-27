"""
Module contains a SME class that inherits from Provider class. SME class is an implementation specific to the
peculiarities of the SME feeds and the processing they require that is not common to all providers.
"""
from doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from doit_PowerOutage_ProviderClasses import Outage
from doit_PowerOutage_ProviderClasses import Provider


class SME(Provider):
    """
    SME specific functionality and variables for handling SME feed data. Inherits from Provider.
    """

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.area_list = None

    def extract_areas_list(self):
        """
        Extract the county or zip area information from a json response.
        :return: None
        """
        data_json = self.data_feed_response.json()
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json,
                                                          attribute_name="file_data")
        areas_list_outer = DOIT_UTIL.extract_attribute_from_dict(data_dict=file_data,
                                                                 attribute_name="areas")
        areas_list_dict = areas_list_outer[0]
        areas_list_inner = DOIT_UTIL.extract_attribute_from_dict(data_dict=areas_list_dict,
                                                                 attribute_name="areas")
        self.area_list = areas_list_inner
        return

    def extract_outage_counts(self):
        """
        Extract the outage counts from the outage areas dataset json and build stat objects to store the data.
        :return: None
        """
        list_of_stats_objects = []
        for county_dict in self.area_list:
            county = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
            outages_dict = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="cust_a")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=outages_dict, attribute_name="val")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="cust_s")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=county,
                                                outages=outages,
                                                customers=customers,
                                                state=DOIT_UTIL.MARYLAND))
        self.stats_objects = list_of_stats_objects
        return
