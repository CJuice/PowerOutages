"""
Module contains a FES class that inherits from Provider class. FES class is an implementation specific to the
peculiarities of the FES feeds and the processing they require that is not common to all providers.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider


class FES(Provider):
    """
    FES specific functionality and variables for handling FES feed data. Inherits from Provider.
    FES does not report customer counts for zip codes.
    """
    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.zip_events_list = None
        self.area_elements = None
        self.stats_data_tuples_list = None

    def create_stats_objects(self):
        """
        Build stat objects
        :return:
        """
        list_of_stats_objects = []
        for stat_tup in self.stats_data_tuples_list:
            area, customers, outages = stat_tup
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=area,
                                                outages=outages,
                                                customers=customers,
                                                state=DOIT_UTIL.MARYLAND))
        self.stats_objects = list_of_stats_objects
        return

    def extract_area_outage_elements(self):
        """
        Extract the area outage elements from the xml response
        :return: none
        """
        area_elements_list = []
        for area_element in self.xml_element.iter("Outage"):
            area_elements_list.append(area_element)
        self.area_elements = area_elements_list
        return

    def extract_date_created(self):
        """
        Extract the data created from the xml response
        :return: none
        """
        response_header_element = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=self.xml_element,
                                                                                               tag_name="ResponseHeader")
        date_created = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=response_header_element,
                                                                                    tag_name="CreateDateTime")
        self.date_created = date_created.text
        return

    def extract_outage_counts(self):
        """
        Extract outage counts from the xml response and clean the county string
        :return: none
        """
        stats_tuples_list = []
        for element in self.area_elements:
            area = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=element,
                                                                                tag_name=self.style.title()).text
            outages = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=element,
                                                                                   tag_name="CustomersOut").text
            if self.style == DOIT_UTIL.COUNTY:
                customers = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=element,
                                                                                         tag_name="CustomersServed").text
            else:
                customers = -9999

            if self.style == DOIT_UTIL.COUNTY and "(MD)" not in area:
                # Isolating MD counties. NOTE: Non-MD zip codes are not filtered out here.
                continue

            area = area.replace("(MD)", "")
            stats_tuples_list.append((area, customers, outages))

        self.stats_data_tuples_list = stats_tuples_list
        return
