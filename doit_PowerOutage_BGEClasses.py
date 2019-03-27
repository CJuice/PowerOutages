"""
Module contains a BGE class that inherits from Provider class. BGE class is an implementation specific to the
peculiarities of the BGE feeds and the processing they require that is not common to all providers.
"""
from doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from doit_PowerOutage_ProviderClasses import Outage
from doit_PowerOutage_ProviderClasses import Provider
import doit_PowerOutage_CentralizedVariables as VARS


class BGE(Provider):
    """
    BGE specific functionality and variables for handling BGE feed data. Inherits from Provider.
    BGE uses a POST rather than GET for retrieving feed data, unlike the other providers. This requires unique
    functionality that this class provides.
    """

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
        self.outages_list = None

    def build_extra_header_for_SOAP_request(self) -> dict:
        """
        Build the extra header required for the SOAP request
        :return: dictionary
        """
        return {"Content-Type": "text/xml", "charset": "utf-8", "SOAPAction": self.soap_header_uri, }

    def extract_date_created(self):
        """
        Extract the date created from the xml response content
        :return: none
        """
        for date_time in self.xml_element.iter("CreateDateTime"):
            self.date_created = date_time.text
            return

    def extract_outage_counts(self):
        """
        Extract the outage counts from xml.
        NOTE: It appears that BGE does not provide a count of customers served for zip code areas. Set to -9999.
        :return:
        """
        substitution = {"County": "County", "ZIP": "ZipCode"}.get(self.style)
        stats_objects_list = []
        for outage in self.outages_list:
            area = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=outage,
                                                                                tag_name=substitution).text
            outages = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=outage,
                                                                                   tag_name="CustomersOut").text
            if self.style == "ZIP":
                customers = VARS.database_flag
            else:
                customers = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=outage,
                                                                                         tag_name="CustomersServed").text
            stats_objects_list.append(Outage(abbrev=self.abbrev,
                                             style=self.style,
                                             area=area,
                                             outages=outages,
                                             customers=customers,
                                             state=DOIT_UTIL.MARYLAND))
        self.stats_objects = stats_objects_list
        return

    def extract_outage_elements(self):
        """
        Extract the outage elements from the response content
        :return: none
        """
        outage_elements_list = []
        for outage in self.xml_element.iter("Outage"):
            outage_elements_list.append(outage)
        self.outages_list = outage_elements_list
        return
