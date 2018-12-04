"""
Module contains a DEL class that inherits from PEPDELParent class which inherits from Provider class. 
DEL class is an implementation specific to the peculiarities of the DEL feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. DEL inherits from the PEPDELParent class.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent


class DEL(PEPDELParent):
    """
    DEL specific functionality and variables for handling DEL feed data. Inherits from PEPDELParent and therefore
    Provider. DEL has unique requirements related to zip codes.
    """

    def __init__(self, provider_abbrev, style):
        super(DEL, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.SPECIAL_ZIP_VALUES_DICT = {"21921,21922": "21916,21920,21921"}

    def process_grouped_zip_code_values(self):
        for stat_obj in self.stats_objects:
            if self.style == "ZIP":

                # Substitute comma separated strings of zipcodes from special values dict, if value found.
                try:
                    stat_obj.area = self.SPECIAL_ZIP_VALUES_DICT[stat_obj.area]
                    print(f"{self.abbrev} - FOUND: {stat_obj.area}")
                except KeyError as ke:
                    print(f"{self.abbrev} - NOT FOUND: {stat_obj.area}")
        return
