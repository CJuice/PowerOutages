"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util


class DEL(Provider, PEPDELParent):
    def __init__(self, provider_abbrev):
        super(DEL, self).__init__(provider_abbrev=provider_abbrev)