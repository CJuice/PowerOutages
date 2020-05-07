"""
Module contains a PEP class that inherits from PEPDELParent class which inherits from Provider class.
PEP class is an implementation specific to the peculiarities of the DEL feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. PEP inherits from the PEPDELParent class.
"""
import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent


class PEP(PEPDELParent):
    """
    PEP specific functionality and variables for handling PEP feed data. Inherits from PEPDELParent and therefore
    Provider.
    """
    def __init__(self, provider_abbrev, style):
        super(PEP, self).__init__(provider_abbrev=provider_abbrev, style=style)

    def extract_county_outage_lists_by_state(self):
        """
        TODO: update documentation, also make assumption that pepco only covers md and dc. describe issues and reason
            for the special handling

        :return: none
        """
        dc_areas_list = []
        md_areas_list = []
        if self.style == DOIT_UTIL.COUNTY:

            # Need to build a single list of aggregated dicts. One for DC and one for MD
            for area_dict in self.area_list:
                area_name = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="name")
                if area_name.lower() == DOIT_UTIL.DISTRICT_OF_COLUMBIA.lower():
                    dc_areas_list.append(area_dict)
                else:
                    md_areas_list.append(area_dict)

            # # Need to store the DC and MD dicts with key to make states_outages_list_dict
            # self.state_to_data_list_dict = {"DC": dc_areas_list, "MD": md_areas_list}
        else:
            # TODO: No state given in json, must determine if in DC. Can't assign all to MD.
            for area_dict in self.area_list:
                if area_dict.get("name") in VARS.district_of_columbia_exelon_defined_aggregated_zip_codes_values:
                    dc_areas_list.append(area_dict)
                else:
                    md_areas_list.append(area_dict)

        # Need to store the DC and MD dicts with key to make states_outages_list_dict
        self.state_to_data_list_dict = {"DC": dc_areas_list, "MD": md_areas_list}
        return
