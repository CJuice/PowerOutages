"""
Module contains a BGE class that inherits from Provider class. BGE class is an implementation specific to the
peculiarities of the BGE feeds and the processing they require that is not common to all providers.
"""

from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
# from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_Kubra_ParentClass import KubraParent

import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS


class BGE(KubraParent):
    """
    BGE specific functionality and variables for handling BGE feed data. Inherits from Provider.
    BGE uses a POST rather than GET for retrieving feed data, unlike the other providers. This requires unique
    functionality that this class provides.
    """

    # POST_DATA_XML_STRING = """<?xml version="1.0" encoding="utf-8"?>\n
    # <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:out="http://Constellation.BGE.com/OutageInfoWebService">\n
    # \t<soapenv:Header>\n
    # \t\t<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">\n
    # \t\t\t<wsse:UsernameToken>\n
    # \t\t\t\t<wsse:Username>{username}</wsse:Username>\n
    # \t\t\t\t<wsse:Password>{password}</wsse:Password>\n
    # \t\t\t</wsse:UsernameToken>\n
    # \t\t</wsse:Security>\n
    # \t</soapenv:Header>\n
    # \t<soapenv:Body>\n
    # \t\t<out:GetCountyAndZipCodeData/>\n
    # \t</soapenv:Body>\n
    # </soapenv:Envelope>
    # """

    def __init__(self, provider_abbrev, style):
        super(BGE, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.outages_list = None
        self.post_uri = None
        self.report_str_template = "public/reports/{report_id}_report.json"
        self.soap_header_uri = None
        self.xml_element = None

    # def build_extra_header_for_SOAP_request(self) -> dict:
    #     """
    #     Build the extra header required for the SOAP request
    #     :return: dict
    #     """
    #     return {"Content-Type": "text/xml", "charset": "utf-8", "SOAPAction": self.soap_header_uri, }

    def extract_date_created(self) -> None:
        """
        Extract the date created from the xml response content
        :return: None
        """
        for date_time in self.xml_element.iter("CreateDateTime"):
            self.date_created = date_time.text
            return

    def extract_outage_counts(self) -> None:
        """
        Extract the outage counts from xml.
        NOTE: It appears that BGE does not provide a count of customers served for zip code areas. Set to -9999.
        :return: None
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

    def extract_outage_elements(self) -> None:
        """
        Extract the outage elements from the response content
        :return: None
        """
        outage_elements_list = []
        for outage in self.xml_element.iter("Outage"):
            outage_elements_list.append(outage)
        self.outages_list = outage_elements_list
        return

    def extract_source_report(self) -> None:
        """
        Extract the source report string value from the configuration feed response json

        BGE is unlike Pep and Del, the report_id is fixed and therefore is not included in the json from
        the call to the configuration url.
        :return: None
        """

        if self.style == DOIT_UTIL.ZIP:
            source_data = self.report_str_template.format(report_id=self.report_id)
        else:
            configuration_json = self.configuration_feed_response.json()
            config_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=configuration_json,
                                                                attribute_name="config")
            reports_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=config_data,
                                                                 attribute_name="reports")
            data_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=reports_data,
                                                              attribute_name="data")
            interval_generation_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_data,
                                                                             attribute_name="interval_generation_data")

            # NOTE: For BGE, expecting len 1 not 2, protect against more should the design change unexpectedly
            county_data, *rest = interval_generation_data
            source_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_data, attribute_name="source")
        self.report_source = source_data
        return

    def extract_area_outage_lists_by_state(self) -> None:
        """
        Extract area outage dicts, assuming all are MD, aggregate into list, and store in state dict.
        BGE json data varied from DPL (DEL) json data. The same functions in the Kubra parent class could not be
        applied. The objects/data of interest was provided at two different levels of the json hierarchy. BGE,
        like PEPCO, did not contain a state level but DEL did. DEL seemed the better design.
        A choice was made to handle the variation in style by overloading the Kubra method in the BGE class. An
        assumption has been made that BGE only covers MD.
        Overload of Kubra_ParentClass method.
        :return: None
        TODO: Attempted to refactor to flatten nested levels. Tried inner functions and ternary etc. Future improvement.
        """
        # dc_areas_list = []
        md_areas_list = []

        for area_dict in self.area_list:

            # Identical for county and zip
            # area_name = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="name")
            md_areas_list.append(area_dict)
            # if self.style == DOIT_UTIL.COUNTY:
            #
            #     # Easy, unlike zip code areas
            #     md_areas_list.append(area_dict)
            # else:
            #
            #     # Need to check each and every zip code in single or multi-zip string.
            #     # During testing did not find scenario where MD and DC zip were in same outage string. Assumption made.
            #     for value in DOIT_UTIL.generate_value_from_csv_string(area_name):
            #         if value in self.md_zips_keys_only:
            #             md_areas_list.append(area_dict)
            #             break
            #         # elif value in VARS.district_of_columbia_zip_code_inventory_from_web:
            #         #     dc_areas_list.append(area_dict)
            #         #     break
            #         else:
            #             # If an unknown zip code is found, print a message and move on to next in string of zips
            #             print(f"UNKNOWN ZIP CODE ({value})\t{area_dict}")
            #             continue

        # Need to store the DC and MD dicts with key to make states_outages_list_dict
        self.state_to_data_list_dict = {"MD": md_areas_list}
        return