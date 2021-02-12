"""
Module contains a DEL class that inherits from PEPDELParent class which inherits from Provider class. 
DEL class is an implementation specific to the peculiarities of the DEL feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. DEL inherits from the PEPDELParent class.
"""

from PowerOutages.doit_PowerOutage_Kubra_ParentClass import KubraParent


class DEL(KubraParent):
    """
    DEL specific functionality and variables for handling DEL feed data. Inherits from PEPDELParent and therefore
    Provider.
    NOTE: DEL and PEP report.json hierarchy are different. Overload extract_area_outage_lists_by_state() for PEP
        but not DEL, to handle hierarchy variation in PEP json. Chose to treat DEL json structure as correct and
        what to expect since it contained a state level, whereas the PEP json went straight to the county level
        and also included the District of Columbia in with the Maryland counties.
    """

    def __init__(self, provider_abbrev, style):
        super(DEL, self).__init__(provider_abbrev=provider_abbrev, style=style)
        # self.SPECIAL_ZIP_VALUES_DICT = {"21921,21922": "21916,21920,21921"}
