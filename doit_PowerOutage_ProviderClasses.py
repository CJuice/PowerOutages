"""

"""
from dataclasses import dataclass
from datetime import datetime
import PowerOutages_V2.doit_PowerOutage_WebRelatedFunctionality as WebFunc


class Provider:
    COUNTY_DB_DELETE_STATEMENT = """"exec RealTime_DeletePowerOutagesCounty '{prov_abbrev}', 'county'"""
    COUNTY_DB_UPDATE_STATEMENT = """exec RealTime_UpdatePowerOutagesCounty {outage}, '{county}', '{prov_abbrev}', '{state}'"""
    ZIP_DB_DELETE_STATEMENT = """"exec RealTime_DeletePowerOutagesCounty '{prov_abbrev}', 'zip'""" # Uses County proced.
    ZIP_DB_UPDATE_STATEMENT = """exec RealTime_UpdatePowerOutagesZip {outage}, '{zip_code}', '{prov_abbrev}'"""

    def __init__(self, provider_abbrev: str, style: str):
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
        self.style = style
        self.stats_objects = None
        self.sql_insert_record_county = """"INSERT INTO dbo.RealTime_PowerOutagesCounty(state, county, outage, provider, updated, created)
        VALUES ({state},{county},{outages},{abbrev},{date_updated},{date_created})"""
        self.sql_insert_record_zip = """"INSERT INTO dbo.RealTime_PowerOutagesZipcodes(ZIPCODE, PROVIDER, OUTAGE, CREATED, UPDATED)
                VALUES ({area},{abbrev},{outages},{date_created},{date_updated})"""
        # self.util_class = UtilFunc.Utility
        # self.prov_json_class = ProviderJSON
        # self.prov_xml_class = ProviderXML
        self.web_func_class = WebFunc.WebFunctionality

    # TODO: Convert the date created value, provided in/by the data feeds, to a datetime object. Needed for database entry and JSON output file format

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

    def insert_records_into_database_table(self, db_connection, db_cursor):
        date_updated = Provider.current_date_time()
        for obj in self.stats_objects:
            if self.style == "ZIP":
                sql = self.sql_insert_record_zip.format(area=obj.area,
                                                        abbrev=obj.abbrev,
                                                        outages=obj.outages,
                                                        date_created=self.date_created,
                                                        date_updated=date_updated
                                                        )
            else:
                sql = self.sql_insert_record_county.format(state=obj.state,
                                                           county=obj.area,
                                                           outages=obj.outages,
                                                           abbrev=self.abbrev,
                                                           date_updated=date_updated,
                                                           date_created=self.date_created
                                                           )
            db_cursor.execute(sql)
        db_connection.commit()
        return


@dataclass
class Outage:
    abbrev: str
    style: str
    area: str
    outages: int
    customers: int
    state: str