"""

"""
from datetime import datetime
from dataclasses import dataclass
# from xml.dom.minidom import parseString
import configparser
import json
import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebFunc
import xml.dom.minidom
import xml.etree.ElementTree as ET


class Provider:

    def __init__(self, provider_abbrev: str):
        self.abbrev = provider_abbrev
        self.date_created_response = None
        self.data_feed_uri = None
        self.data_feed_response = None
        self.date_created_uri = None
        self.maryland = "Maryland"
        self.metadata_feed_response = None
        self.metadata_feed_uri = None
        self.metadata_key = None
        self.metadata_key_attribute = "directory"
        self.prov_json_class = ProviderJSON
        self.prov_xml_class = ProviderXML
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
    def parse_xml_response_to_element(response_xml_str: str) -> ET.Element:
        try:
            # print(response_xml_str)
            x = ET.fromstring(response_xml_str)
            # print(x)
            # return ET.fromstring(response_xml_str)
            return x
        except Exception as e:
            print(f"Unable to process xml response to Element using ET.fromstring(): {e}")
            exit()

    @staticmethod
    def extract_metadata_attribute_value_from_xml_element(root_element: ET.Element) -> str:
        return root_element[0].text

    #
    # @staticmethod
    # def convert_xml_response_to_DOM(response_xml_str: str) -> xml.dom.minidom.Document:
    #     try:
    #         return xml.dom.minidom.parseString(response_xml_str)
    #     except Exception as e:
    #         print(f"Unable to process xml response to DOM using parseString(): {e}")
    #         exit()
    #
    # @staticmethod
    # def extract_xml_tag_element(xml_dom: xml.dom.minidom.Document, tag_name: str, tag_index: int = 0) -> xml.dom.minidom.Element:
    #     try:
    #         return xml_dom.getElementsByTagName(tag_name)[tag_index]
    #     except Exception as e:  # TODO: Improve exception handling
    #         print(e)
    #         exit()
    #
    # @staticmethod
    # def extract_attribute_from_xml_tag_element(xml_element: xml.dom.minidom.Element, attribute_name: str) -> str:
    #     # print(f"func: {xml_element}, {attribute_name}")
    #     try:
    #         return xml_element.getAttribute(attname=attribute_name)
    #         # return xml_element.getElementsByTagName(attribute_name)[0].firstChild.nodeValue
    #     except Exception as e:  # TODO: Improve exception handling
    #         print(e)
    #         exit()


class ProviderJSON:

    @staticmethod
    def process_json_response_to_dict(response_json_str: str) -> dict:
        # raised JSONDecoder exception passes to higher handling that routes xml to separate functionality
        return json.loads(response_json_str)

    @staticmethod
    def extract_attribute_from_dict(metadata_dict: dict, attribute_name: str) -> str:
        try:
            return metadata_dict[attribute_name]
        except KeyError as ke:
            print(f"Unable to extract key from metadata response dict: {e}")
            exit()


@dataclass
class ProviderDetails:
    """
    store details on provider feed and process styles
    dual_feed: indicates whether web response includes data for ZIP and County together (True) or separate (False)
    """
    dual_feed: bool
    style: str