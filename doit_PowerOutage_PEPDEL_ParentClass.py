"""

"""
from dataclasses import dataclass
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider

class PEPDELParent(Provider):

    def __init__(self, provider_abbrev, style):
        super(PEPDELParent, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.area_DEL_list = None
        self.area_DE_dict = None
        self.area_MD_dict = None
        self.area_DC_dict = None
        self.delaware_outages_list = None
        self.delaware_stats_objects = None
        self.maryland_outages_list = None
        self.maryland_stats_objects = None
        self.wash_dc_outages_list = None
        self.wash_dc_stats_objects = None
        self.state_to_data_list_dict = None
        # self.stats_objects_by_county = None
        # self.stats_objects_by_zip = None
        self.stats_objects = None
        self.zip_desc_list = None

    def extract_areas_list_county_process(self, data_json):
        file_data = doit_util.extract_attribute_from_dict(data_dict=data_json,
                                                          attribute_name="file_data")
        curr_custs_aff = doit_util.extract_attribute_from_dict(data_dict=file_data,
                                                               attribute_name="curr_custs_aff")
        file_data = doit_util.extract_attribute_from_dict(data_dict=curr_custs_aff,
                                                          attribute_name="areas")
        area_DEL_dict, *rest = file_data  # Expecting dict len=1, *rest guards against len>1
        self.area_DEL_list = doit_util.extract_attribute_from_dict(data_dict=area_DEL_dict,
                                                                   attribute_name="areas")

    def extract_county_outage_lists_by_state(self):
        states_outages_list_dict = {}
        for state_dict in self.area_DEL_list:
            state_abbrev = doit_util.extract_attribute_from_dict(data_dict=state_dict,
                                                                 attribute_name="area_name")
            states_outages_list_dict[state_abbrev] = doit_util.extract_attribute_from_dict(data_dict=state_dict,
                                                                                           attribute_name="areas")
        self.state_to_data_list_dict = states_outages_list_dict
        return
    # def assign_state_outage_lists(self):
    #     self.delaware_outages_list =

    def extract_outage_counts_by_county(self):
        list_of_stats_objects = []
        for state_abbrev, outages_list in self.state_to_data_list_dict.items():
            for county_dict in outages_list:
                county = doit_util.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
                outages = doit_util.extract_attribute_from_dict(data_dict=county_dict, attribute_name="custs_out")
                customers = doit_util.extract_attribute_from_dict(data_dict=county_dict,
                                                                  attribute_name="total_custs")
                list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                              style=self.style,
                                                              area=county,
                                                              outages=outages,
                                                              customers=customers,
                                                              state=state_abbrev))
        self.stats_objects = list_of_stats_objects
        return

    def extract_zip_descriptions_list(self, data_json):
        self.zip_desc_list = doit_util.extract_attribute_from_dict(data_dict=data_json, attribute_name="file_data")

    def extract_outage_counts_by_zip_desc(self):
        # list_of_stats_objects_by_zip_desc = []
        list_of_stats_objects = []
        for desc in self.zip_desc_list:
            zip_desc_dict, *rest = doit_util.extract_attribute_from_dict(data_dict=desc, attribute_name="desc")
            zip_code = doit_util.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="area_name")
            outages = doit_util.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="custs_out")
            customers = doit_util.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="total_custs")
            state = doit_util.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="state")
            # list_of_stats_objects_by_zip_desc.append(Outage(abbrev=self.abbrev,
            #                                                 style=self.style,
            #                                                 area=zip_code,
            #                                                 outages=outages,
            #                                                 customers=customers,
            #                                                 state=state))
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                            style=self.style,
                                                            area=zip_code,
                                                            outages=outages,
                                                            customers=customers,
                                                            state=state))
        # self.stats_objects_by_zip = list_of_stats_objects_by_zip_desc
        self.stats_objects = list_of_stats_objects

        return
