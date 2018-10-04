"""

"""
from xml.dom.minidom import parseString
from datetime import datetime
import configparser
from dataclasses import dataclass
import xml.dom.minidom
import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebFunc


class Provider:

    def __init__(self, provider_abbrev: str):
        self.abbrev = provider_abbrev
        self.metadata_feed_uri = None
        self.metadata_feed_response = None
        self.data_feed_uri = None
        self.data_feed_response = None
        self.date_created_uri = None
        self.date_created_response = None
        self.maryland = "Maryland"
        self.prov_json_class = ProviderJSON()
        self.prov_xml_class = ProviderXML()
        self.web_func_class = WebFunc.WebFunctionality()
        # self.parser = parser
        # self.dual_feed = dual_feed
        # self.style = style

    @staticmethod
    def get_config_variable(parser, section: str, variable_name: str) -> str:
        try:
            return parser[section][variable_name]
        except KeyError as ke:
            print(f"Section or Variable not found: {section} - {variable_name}")
            exit()
        except Exception as e:  # TODO: Improve exception handling
            print(e)
            exit()

    @staticmethod
    def current_date_time() -> str:
        return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())


class ProviderXML:

    @staticmethod
    def process_xml_response_to_DOM(response_xml_str: str) -> xml.dom.minidom.Document:
        try:
            return parseString(response_xml_str)
        except Exception as e:
            print(f"Unable to process xml response to DOM using parseString(): {e}")

    @staticmethod
    def extract_xml_tag_element(xml_dom: xml.dom.minidom.Document, tag_name: str, tag_index: int = 0) -> xml.dom.minidom.Element:
        try:
            return xml_dom.getElementsByTagName(tag_name)[tag_index]
        except Exception as e:  # TODO: Improve exception handling
            print(e)
            exit()

    @staticmethod
    def extract_attribute_from_xml_tag_element(xml_element: xml.dom.minidom.Element, attribute_name: str) -> str:
        try:
            return xml_element.getAttribute(attribute_name)
        except Exception as e:  # TODO: Improve exception handling
            print(e)
            exit()


@dataclass
class ProviderDetails:
    """
    store details on provider feed and process styles
    dual_feed: indicates whether web response includes data for ZIP and County together (True) or separate (False)
    """
    dual_feed: bool
    style: str

class ProviderJSON:
    pass

