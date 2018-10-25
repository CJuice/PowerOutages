"""

"""
from dataclasses import dataclass
from datetime import datetime
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebFunc
import dateutil.parser


class Provider:

    def __init__(self, provider_abbrev: str, style: str):
        super(Provider, self).__init__()
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
        self.maryland = "Maryland"
        self.metadata_feed_response = None
        self.metadata_feed_response_status_code = None
        self.metadata_feed_uri = None
        self.metadata_key = None
        self.metadata_key_attribute = "directory"
        self.style = style
        self.stats_objects = None
        self.sql_insert_record_county = """INSERT INTO dbo.RealTime_PowerOutagesCounty(STATE, COUNTY, OUTAGE, PROVIDER, UPDATED, CREATED) VALUES ('{state}','{county}',{outages},'{abbrev}','{date_updated}','{date_created}')"""
        self.sql_insert_record_zip = """INSERT INTO dbo.RealTime_PowerOutagesZipcodes(ZIPCODE, PROVIDER, OUTAGE, CREATED, UPDATED) VALUES ('{area}','{abbrev}',{outages},'{date_created}','{date_updated}')"""
        self.web_func_class = WebFunc.WebFunctionality

    def build_output_dict(self, unique_key:str) -> dict:
        return {unique_key: {"data": self.data_feed_response_status_code,
                             "date": self.date_created_feed_response_status_code,
                             "metadata": self.metadata_feed_response_status_code,
                             "created": self.date_created,
                             "data age (min):": self.data_age_minutes,
                             }
                }

    def detect_response_style(self):
        if "xml" in self.data_feed_response.headers["content-type"]:
            self.data_feed_response_style = "XML"
        else:
            self.data_feed_response_style = "JSON"
        return

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

    # TODO: Does this need to be static? Why?
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

    def generate_insert_sql_statement(self):
        self.date_updated = DOIT_UTIL.current_date_time()
        for stat_obj in self.stats_objects:
            if self.style == "ZIP":
                sql = self.sql_insert_record_zip.format(area=stat_obj.area,
                                                        abbrev=stat_obj.abbrev,
                                                        outages=stat_obj.outages,
                                                        date_created=self.date_created,
                                                        date_updated=self.date_updated
                                                        )
            else:
                sql = self.sql_insert_record_county.format(state=stat_obj.state,
                                                           county=stat_obj.area,
                                                           outages=stat_obj.outages,
                                                           abbrev=self.abbrev,
                                                           date_updated=self.date_updated,
                                                           date_created=self.date_created
                                                           )
            yield sql

    def groom_date_created(self):
        # NOTE: Valuable Resource - https://dateutil.readthedocs.io/en/stable/parser.html
        try:
            datetime_object = dateutil.parser.parse(timestr=self.date_created)
        except ValueError as ve:
            print(f"ValueError while parsing date created string to datetime: {self.date_created}\n{ve}")
            self.date_created = datetime.fromisoformat(DOIT_UTIL.ZERO_TIME_STRING)
        except OverflowError as oe:
            print(f"OverflowError while parsing date created string to datetime: {self.date_created}\n{oe}")
            self.date_created = datetime.fromisoformat(DOIT_UTIL.ZERO_TIME_STRING)
        else:
            self.date_created = f"{datetime_object:%Y-%m-%d %H:%M}"

    def calculate_data_age_minutes(self):
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
            self.data_age_minutes = (difference.seconds / 60)


@dataclass
class Outage:
    abbrev: str
    style: str
    area: str
    outages: int
    customers: int
    state: str