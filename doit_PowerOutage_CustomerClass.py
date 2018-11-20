from dataclasses import dataclass
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS


class Customer:

    def __init__(self):
        self.county_customer_count_objects_list = None
        self.sql_update_customer_counts_table = VARS.sql_update_customer_counts_table

    @dataclass
    class CountyCustomerCount:
        area: str
        customers: int

    def calculate_county_customer_counts(self, prov_objects):

        # gather all county stats objects from all providers
        master_stat_obj_list = []
        county_objs = [obj for obj in prov_objects.values() if obj.style == DOIT_UTIL.COUNTY]
        for obj in county_objs:
            master_stat_obj_list.extend(obj.stats_objects)
        county_counts_dict = {county: 0 for county in DOIT_UTIL.MARYLAND_COUNTIES}
        for obj in master_stat_obj_list:
            if obj.state == DOIT_UTIL.MARYLAND:
                county_counts_dict[obj.area] += obj.customers
        county_customer_count_objects_list = [Customer.CountyCustomerCount(area=area, customers=customers) for
                                              area, customers in county_counts_dict.items()]
        self.county_customer_count_objects_list = county_customer_count_objects_list
        return

    def generate_insert_sql_statement_customer_count(self):
        for obj in self.county_customer_count_objects_list:
            database_ready_area_name = obj.area.replace("'", "''")  # Prep apostrophe containing names for DB
            sql = self.sql_update_customer_counts_table.format(cust_count=obj.customers, area=database_ready_area_name)
            yield sql