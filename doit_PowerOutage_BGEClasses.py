"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage


class BGE(Provider):

    POST_DATA_XML_STRING = """<?xml version="1.0" encoding="utf-8"?>\n
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://Constellation.BGE.com/OutageInfoWebService">\n
    \t<soapenv:Header>\n
    \t\t<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">\n
    \t\t\t<wsse:UsernameToken>\n
    \t\t\t\t<wsse:Username>{username}</wsse:Username>\n
    \t\t\t\t<wsse:Password>{password}</wsse:Password>\n
    \t\t\t</wsse:UsernameToken>\n
    \t\t</wsse:Security>\n
    \t</soapenv:Header>\n
    \t<soapenv:Body>\n
    \t\t<out:GetCountyAndZipCodeData/>\n
    \t</soapenv:Body>\n
    </soapenv:Envelope>
    """

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.soap_header_uri = None
        self.post_uri = None
        self.xml_element = None
        self.body_element = None
        self.data_response_element = None
        self.data_result_element = None

    def build_extra_header_for_SOAP_request(self):
        return {"Content-Type": "text/xml","charset": "utf-8","SOAPAction": self.soap_header_uri, }
