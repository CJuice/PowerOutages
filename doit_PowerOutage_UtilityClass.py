from datetime import datetime
import json
import xml.etree.ElementTree as ET
import configparser


class Utility:

    ZERO_TIME_STRING = "00:00:00 00:00:00"
    COUNTY = "County"
    MARYLAND = "Maryland"
    MARYLAND_COUNTIES = ["Allegany", "Anne Arundel", "Baltimore", "Baltimore City", "Calvert", "Caroline", "Carroll",
                         "Cecil", "Charles", "Dorchester", "Frederick", "Garrett", "Harford", "Howard", "Kent",
                         "Montgomery", "Prince George's", "Queen Anne's", "St. Mary's", "Somerset", "Talbot",
                         "Washington", "Wicomico", "Worcester"]
    ZIP = "ZIP"
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

    @staticmethod
    def current_date_time() -> str:
        return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())

    @staticmethod
    def write_to_file(file: str, content):
        with open(file, 'w') as file_handler:
            file_handler.write(json.dumps(content))
        return

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

    @staticmethod
    def extract_all_immediate_child_features_from_element(element: ET.Element, tag_name: str) -> ET.Element:
        try:
            return element.findall(tag_name)
        except AttributeError as ae:
            print(f"AttributeError: Unable to extract '{tag_name}' from {element.text}: {ae}")
            exit()

    @staticmethod
    def extract_first_immediate_child_feature_from_element(element: ET.Element, tag_name: str) -> ET.Element:
        try:
            return element.find(tag_name)
        except AttributeError as ae:
            print(f"AttributeError: Unable to extract '{tag_name}' from {element.text}: {ae}")
            exit()

    @staticmethod
    def extract_attribute_from_dict(data_dict: dict, attribute_name: str):
        try:
            return data_dict[attribute_name]
        except KeyError as ke:
            print(f"KeyError: Unable to extract '{attribute_name}' from {data_dict}: {ke}")
            exit()

    @staticmethod
    def build_feed_uri(metadata_key: str, data_feed_uri: str) -> str:
        return data_feed_uri.format(metadata_key=metadata_key)

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
    def remove_commas_from_counts(objects_list: list):
        for obj in objects_list:
            try:
                obj.outages = obj.outages.replace(",", "")
            except AttributeError as ae:
                # doesn't have .replace method. likely type int
                pass
            try:
                obj.customers = obj.customers.replace(",", "")
            except AttributeError as ae:
                # doesn't have .replace method. likely type int
                pass
        return

    @staticmethod
    def process_outage_counts_to_integers(objects_list: list):
        replacement_values_dict = {"Less than 5": 1, "<5": 1}
        for obj in objects_list:
            try:
                obj.outages = int(obj.outages)
            except ValueError as ve:
                try:
                    obj.outages = replacement_values_dict[obj.outages]
                except KeyError as ke:
                    obj.outages = -9999
        return

    @staticmethod
    def process_customer_counts_to_integers(objects_list: list):
        replacement_values_dict = {"Less than 5": 1, "<5": 1}
        for obj in objects_list:
            try:
                obj.customers = int(obj.customers)
            except ValueError as ve:
                try:
                    obj.customers = replacement_values_dict[obj.customers]
                except KeyError as ke:
                    obj.customers = -9999
        return

    # @staticmethod
    # def change_case_to_title(stats_objects: list):
    #     # Removed use. Causes case errors in apostrophe containing county names. St. Mary's -> St. Mary'S
    #     for obj in stats_objects:
    #         obj.area = obj.area.title()

    @staticmethod
    def revise_county_name_spellings_and_punctuation(stats_objects_list: list):
        corrections_dict = {"Prince Georges": "Prince George's",
                            "St Marys": "St. Mary's",
                            "St Mary's": "St. Mary's",
                            "St. Marys": "St. Mary's",
                            "Queen Annes": "Queen Anne's",
                            "Kent (MD)": "Kent"}
        for obj in stats_objects_list:
            if obj.area.isupper():
                obj.area = obj.area.title()
            else:
                pass
            try:
                obj.area = corrections_dict[obj.area]
            except KeyError as ke:

                # No correction needed per the dict of items as seen above
                continue
        return

    @staticmethod
    def exchange_state_abbrev_for_full_value(value):
        state_abbrev_dict = {"DC": "District Of Columbia", "DE": "Delaware", "MD": "Maryland", }
        try:
            return state_abbrev_dict[value]
        except KeyError as ke:
            return value
