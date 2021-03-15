"""
Module contains a Provider class and an Outage dataclass.
Provider is parent class for all power outage providers and is intended to contain shared functionality to all.
Outage is a data class used to store reported power outage data. The Outage objects are used during database insertion.
Provider is inherited by all of the child power providing company classes.

"""

from dataclasses import dataclass
from datetime import datetime
from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import dateutil.parser
import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS
import PowerOutages.doit_PowerOutage_WebRelatedFunctionality as WebFunc


class Provider:
    """
    Provider is a parent class containing attributes and methods common to all provider specific classes.
    It is inherited by child classes.
    """
    def __init__(self, provider_abbrev: str, style: str):
        self.abbrev = provider_abbrev
        self.date_created = None
        self.date_created_attribute = "date_generated"
        self.date_created_feed_response = None
        self.date_created_feed_response_status_code = None
        self.date_created_feed_uri = None
        self.date_updated = None
        self.data_age_minutes = None
        self.data_feed_response = None
        self.data_feed_response_status_code = None
        self.data_feed_response_style = None
        self.data_feed_uri = None
        self.file_data_attribute = "file_data"
        self.metadata_feed_response = None
        self.metadata_feed_response_status_code = None
        self.metadata_feed_uri = None
        self.metadata_key = None
        self.metadata_key_attribute = "directory"
        self.style = style
        self.stats_objects = None
        self.sql_insert_record_county_realtime = VARS.sql_insert_record_county_realtime
        self.sql_insert_record_zip_realtime = VARS.sql_insert_record_zip_realtime
        self.sql_insert_record_zip_archive = VARS.sql_insert_record_zip_archive
        self.web_func_class = WebFunc.WebFunctionality

    def build_data_feed_uri(self) -> None:
        """
        Build the data feed uri by substituting the metadata key value into the url
        :return: None
        """
        self.data_feed_uri = self.data_feed_uri.format(metadata_key=self.metadata_key)
        return None

    def build_output_dict(self, unique_key:str) -> dict:
        """
        Build a dictionary of stats used in the JSON file for web display of feed status and process health.
        :param unique_key: str value unique to each provider
        :return: dict, dictionary used in json output file.
        """
        return {unique_key: {"data": self.data_feed_response_status_code,
                             "date": self.date_created_feed_response_status_code,
                             "metadata": self.metadata_feed_response_status_code,
                             "created": self.date_created,
                             "data age (min)": self.data_age_minutes,
                             }
                }

    def calculate_data_age_minutes(self) -> None:
        """
        Determine the difference between two date time values.
        NOTE: Did not convert the datetime values involved in difference calculation to be time zone aware.
        :return: None
        """
        try:
            date_create_datetime_object = dateutil.parser.parse(timestr=self.date_created)
        except ValueError as ve:
            print(f"ValueError while parsing date created string to datetime: {self.date_created}\n{ve}")
            self.data_age_minutes = -9999
        except OverflowError as oe:
            print(f"OverflowError while parsing date created string to datetime: {self.date_created}\n{oe}")
            self.data_age_minutes = -9999
        else:
            difference = datetime.now() - date_create_datetime_object
            self.data_age_minutes = round(number=(difference.seconds / 60), ndigits=1)
        return None

    def detect_response_style(self) -> None:
        """
        Detect the style of the feed provided in the http response; XML and JSON in this project.
        :return: None
        """
        if "xml" in self.data_feed_response.headers["content-type"]:
            self.data_feed_response_style = "XML"
        else:
            self.data_feed_response_style = "JSON"
        return None

    def generate_insert_sql_statement_realtime(self):
        """
        Build the insert sql statement for real time data and yield the statement.
        For both County and ZIP data. If is ZIP, then isolate Maryland only so that DE and DC are not written to table
        :return: None
        """
        # TODO: Assess if sql database will take a tz aware datetime value
        self.date_updated = DOIT_UTIL.current_date_time_str()
        for stat_obj in self.stats_objects:
            if self.style == DOIT_UTIL.ZIP:
                sql = self.sql_insert_record_zip_realtime.format(area=stat_obj.area,
                                                                 abbrev=stat_obj.abbrev,
                                                                 outages=stat_obj.outages,
                                                                 date_created=self.date_created,
                                                                 date_updated=self.date_updated
                                                                 )
            else:
                database_ready_area_name = stat_obj.area.replace("'", "''")  # Prep apostrophe containing names for DB
                sql = self.sql_insert_record_county_realtime.format(state=stat_obj.state,
                                                                    county=database_ready_area_name,
                                                                    outages=stat_obj.outages,
                                                                    abbrev=self.abbrev,
                                                                    date_updated=self.date_updated,
                                                                    date_created=self.date_created
                                                                    )
            yield sql

    @staticmethod
    def get_config_variable(parser, section: str, variable_name: str) -> str:
        """
        Get values from a config file.
        :param parser: parser to use in accessing config file contents
        :param section: the name of the section where the variables of interest are located
        :param variable_name: name of the variable sought
        :return: str, the variable from the config file or exit
        """
        try:
            return parser[section][variable_name]
        except KeyError as ke:
            print(f"Section or Variable not found: {section} - {variable_name}")
            exit()
        except Exception as e:  # TODO: Improve exception handling
            print(e)
            exit()

    def groom_date_created(self) -> None:
        """
        Use a dateutil parser to interpret inconsistent/varying date string formats and format them into specific style.
        NOTE: Valuable Resource - https://dateutil.readthedocs.io/en/stable/parser.html
        NOTE: Since date created comes from providers it is not being converted to timezone aware
        :return: None
        """
        try:
            datetime_object = dateutil.parser.parse(timestr=self.date_created)
        except TypeError as te:
            print(f"TypeError while parsing date created string to datetime: {self.date_created}\n{te}")
            self.date_created = datetime.fromisoformat(DOIT_UTIL.ZERO_TIME_STRING)
        except ValueError as ve:
            print(f"ValueError while parsing date created string to datetime: {self.date_created}\n{ve}")
            self.date_created = datetime.fromisoformat(DOIT_UTIL.ZERO_TIME_STRING)
        except OverflowError as oe:
            print(f"OverflowError while parsing date created string to datetime: {self.date_created}\n{oe}")
            self.date_created = datetime.fromisoformat(DOIT_UTIL.ZERO_TIME_STRING)
        else:
            self.date_created = f"{datetime_object:%Y-%m-%d %H:%M}"
        return None

    def perform_feed_status_check_and_notification(self, alert_email_address: str) -> None:
        """
        Check http response status codes for data, date, and metadata feeds, detect non 200 codes, and trigger email.
        This function does rely on the Utility class; It uses the send_feed_status_check_email() function.
        Object attributes begin as None, and unavailable feeds also equate to None, so can't differentiate currently.
        :param alert_email_address: email address to which alerts are sent
        :return: None
        """
        codes_list = [self.data_feed_response_status_code,
                      self.date_created_feed_response_status_code,
                      self.metadata_feed_response_status_code]
        for code in codes_list:
            if code is not None and int(code) != 200:
                DOIT_UTIL.send_feed_status_check_email(data_code=self.data_feed_response_status_code,
                                                       date_code=self.date_created_feed_response_status_code,
                                                       metadata_code=self.metadata_feed_response_status_code,
                                                       prov_abbrev=self.abbrev,
                                                       alert_email_address=alert_email_address)
                return
        return

    def purge_duplicate_stats_objects(self) -> None:
        """
        Eliminate duplicate stats objects in a list
        Note: Outage objects are mutable and can't be added to sets. Used dictionary unique key behavior to purge.
        :return: None
        """
        temp_dict = {}
        for outage in self.stats_objects:
            temp_dict[str(outage)] = outage
        self.stats_objects = list(temp_dict.values())
        return None

    def purge_zero_outage_zip_stats_objects(self) -> None:
        """
        Remove zero zip outage objects from the stats objects so that only counts greater than zero are inserted in db.
        :return: None
        """
        temp_list = [outage for outage in self.stats_objects if outage.style == DOIT_UTIL.ZIP and outage.outages == 0]
        for zero_outage in temp_list:
            self.stats_objects.remove(zero_outage)
        return None

    def remove_non_maryland_stat_objects(self) -> None:
        """
        Detect stats objects for those not in Maryland and delete the objects from the stats objects list
        :return: None
        """
        non_maryland_stat_objects = []

        for stat_obj in self.stats_objects:
            if stat_obj.state != DOIT_UTIL.MARYLAND:
                non_maryland_stat_objects.append(stat_obj)

        for obj in non_maryland_stat_objects:
            self.stats_objects.remove(obj)
        return None

    def set_status_codes(self) -> None:
        """
        Set the status code attribute for the various feed types; data, date created, and metadata.
        Not all providers have all three feed types. Can't assume AttributeError indicates down/unavailable feed.
        :return: None
        """
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
        return None


@dataclass
class Outage:
    """
    Data class for storing power outage report values
    """
    abbrev: str
    style: str
    area: str
    outages: int
    customers: int
    state: str




