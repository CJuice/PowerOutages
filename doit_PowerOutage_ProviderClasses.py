"""

"""
from datetime import datetime
from dataclasses import dataclass
# from xml.dom.minidom import parseString
# import configparser
import json
import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebFunc
# import xml.dom.minidom
import xml.etree.ElementTree as ET


class Provider:

    def __init__(self, provider_abbrev: str):
        super(Provider, self).__init__()
        self.abbrev = provider_abbrev
        self.date_created = None
        self.date_created_attribute = "date_generated"
        self.date_created_feed_response = None
        self.date_created_feed_response_status_code = None
        self.date_created_feed_uri = None
        self.data_feed_response = None
        self.data_feed_response_status_code = None
        self.data_feed_response_style = None
        self.data_feed_uri = None
        self.maryland = "Maryland"
        self.metadata_feed_response = None
        self.metadata_feed_response_status_code = None
        self.metadata_feed_uri = None
        self.metadata_key = None
        self.metadata_key_attribute = "directory"
        self.prov_json_class = ProviderJSON
        self.prov_xml_class = ProviderXML
        self.web_func_class = WebFunc.WebFunctionality()

    def build_output_dict(self, unique_key:str) -> dict:
        return {unique_key: {"data": self.data_feed_response_status_code,
                             "date": self.date_created_feed_response_status_code,
                             "metadata": self.metadata_feed_response_status_code,
                             "created": self.date_created,
                             }
                }

    def detect_response_style(self):
        if "xml" in self.data_feed_response.headers["content-type"]:
            self.data_feed_response_style = "XML"
        else:
            self.data_feed_response_style = "JSON"
        return

    # def extract_outage_count(self):
    #     pass

    def set_status_codes(self):
        try:
            self.data_feed_response_status_code = self.data_feed_response.status_code
        except AttributeError as ae:
            # no data feed response
            pass
        try:
            self.date_created_feed_response_status_code = self.date_created_feed_response.status_code
        except AttributeError as ae:
            # no date created response
            pass
        try:
            self.metadata_feed_response_status_code = self.metadata_feed_response.status_code
        except AttributeError as ae:
            # no metadata feed response
            pass
        return

    @staticmethod
    def build_feed_uri(metadata_key: str, data_feed_uri: str) -> str:
        return data_feed_uri.format(metadata_key=metadata_key)

    @staticmethod
    def current_date_time() -> str:
        return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())

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


class ProviderXML:

    @staticmethod
    def parse_xml_response_to_element(response_xml_str: str) -> ET.Element:
        try:
            return ET.fromstring(response_xml_str)
        except Exception as e:  # TODO: Improve exception handling
            print(f"Unable to process xml response to Element using ET.fromstring(): {e}")
            exit()

    @staticmethod
    def extract_attribute_value_from_xml_element_by_index(root_element: ET.Element, index_position: int = 0) -> str:
        return root_element[index_position].text


class ProviderJSON:

    @staticmethod
    def process_json_response_to_dict(response_json_str: str) -> dict:
        # raised JSONDecoder exception passes to higher handling that routes xml to separate functionality
        return json.loads(response_json_str)

    @staticmethod
    def extract_attribute_from_dict(data_dict: dict, attribute_name: str):
        try:
            return data_dict[attribute_name]
        except KeyError as ke:
            print(f"KeyError: Unable to extract key from dict: {ke}")
            exit()


@dataclass
class ProviderDetails:
    """
    store details on provider feed and process styles
    dual_feed: indicates whether web response includes data for ZIP and County together (True) or separate (False)
    """
    dual_feed: bool
    style: str

