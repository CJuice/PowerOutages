"""
Module contains a PEP class that inherits from PEPDELParent class which inherits from Provider class.
PEP class is an implementation specific to the peculiarities of the DEL feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. PEP inherits from the PEPDELParent class.
"""
from doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent


class PEP(PEPDELParent):
    """
    PEP specific functionality and variables for handling PEP feed data. Inherits from PEPDELParent and therefore
    Provider.
    """
    def __init__(self, provider_abbrev, style):
        super(PEP, self).__init__(provider_abbrev=provider_abbrev, style=style)
