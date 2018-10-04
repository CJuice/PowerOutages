"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider


class BGE(Provider):

    def __init__(self, provider_abbrev):
        super().__init__(provider_abbrev=provider_abbrev)
        self.soap_header_uri = None
        self.post_data_file = None
        self.post_uri = None
