"""
Module contains a PEP class that inherits from KubraParent class which inherits from Provider class.
PEP class is an implementation specific to the peculiarities of the PEP feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. KubraParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. PEP inherits from the KubraParent class.
TODO: Future, Will need to incorporate zip code points. May want to centralize master inventory of zips for point & poly
"""

import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS
from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages.doit_PowerOutage_Kubra_ParentClass import KubraParent


class PEP(KubraParent):
    """
    PEP specific functionality and variables for handling PEP feed data. Inherits from KubraParent and therefore
    Provider.
    """

    def __init__(self, provider_abbrev, style):
        super(PEP, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.md_zips_keys_only = None

    @property
    def md_zips_keys_only(self):
        """
        Get the md zip codes key value
        :return: None or list depending on object style (Zip or County)
        """
        return self.__md_zips_keys_only

    @md_zips_keys_only.setter
    def md_zips_keys_only(self, value):
        """
        Assign a list of maryland master inventory keys to attribute if the style is ZIP.
        Do not need to perform this functionality if the object is style of COUNTY
        :param value: expected signature, not used
        :return: None
        """
        if self.style == DOIT_UTIL.ZIP:
            self.__md_zips_keys_only = list(VARS.maryland_master_inventory_zip_codes_polygon_geometry.keys())

    def extract_area_outage_lists_by_state(self) -> None:
        """
        Extract area outage dicts, determine state (MD/DC), aggregate into respective lists, and store in state dict.
        PEPCO json data varied from DPL (DEL) json data. The same functions in the Kubra parent class could not be
        applied to both provider feeds (county & zip). The objects/data of interest was provided at two different
        levels of the json hierarchy. PEPCO did not contain a state level but DEL did. DEL seemed the better design.
        A choice was made to handle the variation in style by overloading the Kubra method in the PEP class. An
        assumption has been made that PEPCO only covers MD and DC.
        Overload of Kubra_ParentClass method.
        :return: None
        TODO: Attempted to refactor to flatten nested levels. Tried inner functions and ternary etc. Future improvement.
        """
        dc_areas_list = []
        md_areas_list = []

        for area_dict in self.area_list:

            # Identical for county and zip
            area_name = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="name")

            if self.style == DOIT_UTIL.COUNTY:

                # Easy either or situation, unlike zip code areas
                dc_areas_list.append(area_dict) if area_name.lower() == DOIT_UTIL.DISTRICT_OF_COLUMBIA.lower() else md_areas_list.append(area_dict)
            else:

                # Need to check each and every zip code in single or multi-zip string.
                # During testing did not find scenario where MD and DC zip were in same outage string. Assumption made.
                for value in DOIT_UTIL.generate_value_from_csv_string(area_name):
                    if value in self.md_zips_keys_only:
                        md_areas_list.append(area_dict)
                        break
                    elif value in VARS.district_of_columbia_zip_code_inventory_from_web:
                        dc_areas_list.append(area_dict)
                        break
                    else:
                        # If an unknown zip code is found, print a message and move on to next in string of zips
                        print(f"UNKNOWN ZIP CODE ({value})\t{area_dict}")
                        continue

        # Need to store the DC and MD dicts with key to make states_outages_list_dict
        self.state_to_data_list_dict = {"DC": dc_areas_list, "MD": md_areas_list}
        return None
