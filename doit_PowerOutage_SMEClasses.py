"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import sqlite3
import os
import copy


class SME(Provider):
    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.area = None
        self.outage_events_list = None
        self.desc_list = None
        self.default_zero_count_county_stat_objects = None
        self.memory_count_value_stat_objects = None
        self.cust_count_memory_count_selection = None
        self.updated_amend_objects_from_live_data = None
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

    def create_default_county_outage_stat_objects(self):

        names_count_dict = {"Calvert": 0, "Charles": 0, "Queen Anne's": 0, "St. Mary's": 0}
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
        return

    def county_customer_count_database_safety_check(self):
        # TODO: extrac the sql statements to attributes and use formatting to fill them out
        # Need to check for database existence first, then create db if needed.
        if os.path.exists(self.database_path):
            return
        else:
            # This is important if the database does not exist. Builds and populates default database
            # As of 20181115 SME did not provide county data in data feed when outage count was zero. So no records built.
            try:
                conn = sqlite3.connect(database=self.database_path)
                db_curs = conn.cursor()
                db_curs.execute("""CREATE TABLE :table_name (County_ID integer primary key autoincrement, County_Name text, Customer_Count integer, Last_Updated text)""",
                                {"table_name": self.database_table_name})
                conn.commit()
            except sqlite3.OperationalError as sqlOpErr:
                print(sqlOpErr)
                exit()
            except Exception as e:
                print(e)
                exit()
            else:
                for default_county_stat_obj in self.default_zero_count_county_stat_objects:
                    print(f"Default Object: {default_county_stat_obj}")
                    db_curs.execute("""INSERT INTO :table_name VALUES (Null, :county_name, :cust_count, :date_updated)""",
                                    {"table_name": self.database_table_name,
                                     "county_name": default_county_stat_obj.area,
                                     "cust_count": default_county_stat_obj.customers,
                                     "date_updated": DOIT_UTIL.current_date_time()})
                conn.commit()
                print(f"{self.database_path} did not appear to exist. A new zero count version has been created. Memory of previous SME customer counts has been lost.")
            finally:
                conn.close()
        return

    def get_current_county_customer_counts_in_memory(self):

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

    def amend_default_stat_objects_with_cust_counts_from_memory(self):
        amended_objects_list = []
        memory_county_cust_counts_dict = {name: count for id, name, count in self.cust_count_memory_count_selection}
        for default_stat_obj in self.default_zero_count_county_stat_objects:
            try:
                # Use the default stat objects county name to pull the appropriate memory customer count value
                memory_count_value = memory_county_cust_counts_dict[default_stat_obj.area]
            except KeyError as ke:
                # A spelling error mismatch between default county name and memory spelling of county name
                print(f"Key [{default_stat_obj.area}] not found in county names in memory records: {ke}")
            else:
                # Need to make a new object instead of modifying defaults. Defaults should remain as-built for clarity.
                amended_stat_object = Outage(abbrev=self.abbrev,
                                             style=self.style,
                                             area=default_stat_obj.area,
                                             outages=default_stat_obj.outages,
                                             customers=memory_count_value,
                                             state=self.maryland)
                amended_objects_list.append(amended_stat_object)
        self.memory_count_value_stat_objects = amended_objects_list
        return

    def update_amended_cust_count_objects_using_live_data(self):
        memory_amended_dict = {}
        feed_data_dict = {}
        for amended_obj in self.memory_count_value_stat_objects:

            # Copying objects, otherwise the memory_count_value_stat_objects are modified and this gets confusing
            memory_amended_dict[amended_obj.area] = copy.copy(amended_obj)

        # Need dictionary with county name and corresponding stat object, for those counties actually available in feed
        for stat_obj in self.stats_objects:
            feed_data_dict[stat_obj.area] = stat_obj

        # Need to connect the two realms through their key (county name)
        for county_name_amended, obj_amended in memory_amended_dict.items():
            try:
                feed_stat_obj = feed_data_dict[county_name_amended]
                print(f"SME County Data Feed: {county_name_amended} was present. Customer Count: {feed_stat_obj.customers}")
            except KeyError as ke:

                # feed data dict doesn't have the county object, which means that county was not in the data feed
                print(f"{county_name_amended} data must NOT have be present. Customer Count: {obj_amended.customers} *MEMORY.")
            else:

                # using available feed data customer count value, update the amended objects customer count value
                obj_amended.customers = feed_stat_obj.customers
                obj_amended.outages = feed_stat_obj.outages
        self.updated_amend_objects_from_live_data = memory_amended_dict.values()
        return

    def replace_data_feed_stat_objects_with_amended_objects(self):
        self.stats_objects = self.updated_amend_objects_from_live_data
        return

    def update_sqlite3_cust_count_memory_database(self):
        # TODO: Redesign sql statements to use dictionary syntax. Also extract to attribute
        # Need a dictionary with county name and customer count from value in database
        memory_count_dict = {}
        for obj in self.memory_count_value_stat_objects:
            memory_count_dict[obj.area] = obj.customers
        try:
            conn = sqlite3.connect(database=self.database_path)
            db_curs = conn.cursor()
            for stat_obj in self.stats_objects:
                if stat_obj.customers == memory_count_dict[stat_obj.area]:
                    print(f"{stat_obj.abbrev} customer count value did not change for {stat_obj.area} county.")
                else:
                    database_ready_area_name = stat_obj.area.replace("'", "''")  # Prep apostrophe containing names for DB
                    statement = f"""UPDATE SME_Customer_Count_Memory SET Customer_Count = {stat_obj.customers}, Last_Updated = '{DOIT_UTIL.current_date_time()}' WHERE County_Name = '{database_ready_area_name}'"""
                    db_curs.execute(statement)
                    conn.commit()
                    print(f"{stat_obj.abbrev} customer count value changed. Value in memory was updated from {memory_count_dict[stat_obj.area]} to {stat_obj.customers}.")
        except sqlite3.OperationalError as sqlOpErr:
            print(sqlOpErr)
            exit()
        except Exception as e:
            print(e)
            exit()
        else:
            conn.commit()
        finally:
            conn.close()
        print("SME customer count data updated from data feed.")

        return
