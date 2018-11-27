"""
Module contains a PEPDELParent class that inherits from Provider class. PEPDELParent class is an implementation
specific to the peculiarities of the DEL and PEP feeds and the processing they require that is not common to all
providers but common to them both. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider


class PEPDELParent(Provider):
    """
    Functionality and variables common to the PEP and DEL providers. Inherits from Provider. Portions are overridden
    in the PEP and DEL classes.
    """
    def __init__(self, provider_abbrev, style):
        super(PEPDELParent, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.area_list = None
        self.state_to_data_list_dict = None
        self.zip_desc_list = None

    def extract_areas_list_county(self):
        """
        Extract the county area information from a json response.
        :return: none
        """
        data_json = self.data_feed_response.json()
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json,
                                                          attribute_name="file_data")
        curr_custs_aff = DOIT_UTIL.extract_attribute_from_dict(data_dict=file_data,
                                                               attribute_name="curr_custs_aff")
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=curr_custs_aff,
                                                          attribute_name="areas")
        area_dict, *rest = file_data  # Expecting dict len=1, *rest guards against len>1
        self.area_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict,
                                                               attribute_name="areas")
        return

    def extract_county_outage_lists_by_state(self):
        """
        Extract county outage lists by state from dictionary
        :return: none
        """
        states_outages_list_dict = {}
        for state_dict in self.area_list:
            state_abbrev = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                 attribute_name="area_name")
            states_outages_list_dict[state_abbrev] = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                                           attribute_name="areas")
        self.state_to_data_list_dict = states_outages_list_dict
        return

    def extract_outage_counts_by_county(self):
        """
        Extract outage counts by county from the outage dictionary, exchange state abbreviation for full name, and
        build stat objects
        :return: none
        """
        list_of_stats_objects = []
        for state_abbrev, outages_list in self.state_to_data_list_dict.items():
            state = DOIT_UTIL.exchange_state_abbrev_for_full_value(abbrev=state_abbrev)
            for county_dict in outages_list:
                county = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
                outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="custs_out")
                customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict,
                                                                  attribute_name="total_custs")
                list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                    style=self.style,
                                                    area=county,
                                                    outages=outages,
                                                    customers=customers,
                                                    state=state))
        self.stats_objects = list_of_stats_objects
        return

    def extract_zip_descriptions_list(self):
        """
        Extract zip descriptions list from response json
        :return: none
        """
        data_json = self.data_feed_response.json()
        self.zip_desc_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json, attribute_name="file_data")
        return

    def extract_outage_counts_by_zip_desc(self):
        """
        Extract the outage counts by zip and build stat objects
        :return: none
        """
        list_of_stats_objects = []
        for desc in self.zip_desc_list:
            zip_desc_dict, *rest = DOIT_UTIL.extract_attribute_from_dict(data_dict=desc, attribute_name="desc")
            zip_code = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="area_name")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="custs_out")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="total_custs")
            state = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="state")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=zip_code,
                                                outages=outages,
                                                customers=customers,
                                                state=state))
        self.stats_objects = list_of_stats_objects

        return
