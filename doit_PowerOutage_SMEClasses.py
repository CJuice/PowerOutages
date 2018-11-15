"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import sqlite3
import os


class SME(Provider):
    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.area = None
        self.outage_events_list = None
        self.desc_list = None
        self.default_zero_count_county_stat_objects = None
        self.cust_count_memory_count_selection = None
        self.sme_customer_count_database_name = "SME_Customer_Count_Memory_DB.db"
        self.database_path = os.path.join(os.path.dirname(__file__), "SME_Customer_Count_Memory_DB", self.sme_customer_count_database_name)
        self.database_table_name = "SME_Customer_Count_Memory"

    def extract_outage_events_list(self):
        data_json = self.data_feed_response.json()
        self.outage_events_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json, attribute_name="file_data")

    def extract_outage_counts_by_desc(self):
        list_of_stats_objects = []
        for obj in self.outage_events_list:
            desc_dict = DOIT_UTIL.extract_attribute_from_dict(data_dict=obj, attribute_name="desc")
            area = DOIT_UTIL.extract_attribute_from_dict(data_dict=obj, attribute_name="id")
            cust_affected_dict = DOIT_UTIL.extract_attribute_from_dict(data_dict=desc_dict, attribute_name="cust_a")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=cust_affected_dict, attribute_name="val")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=desc_dict, attribute_name="cust_s")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=area,
                                                outages=outages,
                                                customers=customers,
                                                state=self.maryland))
        self.stats_objects = list_of_stats_objects
        return

    def get_current_county_customer_county_in_memory(self):
        if self.style == DOIT_UTIL.ZIP:
            return
        # Need the previous customer counts
        try:
            conn = sqlite3.connect(database=self.database_path)
            db_curs = conn.cursor()
            db_curs.execute("""SELECT County_ID, County_Name, Customer_Count FROM SME_Customer_Count_Memory""")
        except sqlite3.OperationalError as sqlOpErr:
            print(sqlOpErr)
            exit()
        except Exception as e:
            print(e)
            exit()
        else:
            self.cust_count_memory_count_selection = db_curs.fetchall()  # returns a list of tuples
        finally:
            conn.close()

    def county_customer_count_database_safety_check(self):
        if self.style == DOIT_UTIL.ZIP:
            return

        # check for database existence first, then create db if needed.
        if os.path.exists(self.database_path):
            return
        else:
            # This is important if the database does not exist. Builds and populates default database
            # As of 20181115 SME did not provide county data in data feed when outage count was zero. So no records built.
            names_count_dict = {"Charles": 0, "Queen Anne's": 0, "St. Mary's": 0}
            outages = 0
            stat_objects_list = []
            for name, cust_count in names_count_dict.items():
                stat_objects_list.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=name,
                                                outages=outages,
                                                customers=cust_count,
                                                state=self.maryland))
            self.default_zero_count_county_stat_objects = stat_objects_list

            try:
                conn = sqlite3.connect(database=self.database_path)
                db_curs = conn.cursor()
                db_curs.execute(f"""CREATE TABLE {self.database_table_name} (
                            County_ID integer primary key autoincrement,
                            County_Name text,
                            Customer_Count integer
                            )""")
                conn.commit()
            except sqlite3.OperationalError as sqlOpErr:
                print(sqlOpErr)
                exit()
            except Exception as e:
                print(e)
                exit()
            else:
                for default_county_stat_obj in self.default_zero_count_county_stat_objects:
                    print(default_county_stat_obj)
                    db_curs.execute(f"""INSERT INTO {self.database_table_name} VALUES (Null, :county_name, :cust_count)""",
                                    {"county_name": default_county_stat_obj.area, "cust_count": default_county_stat_obj.customers})
                conn.commit()
                print(f"{self.database_path} did not appear to exist. A new zero count version has been created. Memory of previous SME customer counts has been lost.")
            finally:
                conn.close()
        return


