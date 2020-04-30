"""
The Customer module contains a Customer class. The class is built for the customer count functionality in the
power outage process. A static table of customer counts per county was maintained. The Customer class is used to store
real time data on customer counts from data feeds and update the Customer Count table using the latest feed data rather
than hard coded values of unknown age.
"""
from dataclasses import dataclass
from doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import doit_PowerOutage_CentralizedVariables as VARS


class Customer:
    """
    For storing customer count data from each provider and the county to which the counts apply.
    Contains a data class called CountyCustomerCount that is used to create count objects for values reported by
    power providers in their feed.
    """

    def __init__(self):
        self.county_customer_count_objects_list = None
        self.sql_update_customer_counts_table = VARS.sql_update_customer_counts_table

    @dataclass
    class CountyCustomerCount:
        """
        Data class for storing the county and the total count of customers.
        """
        area: str
        customers: int

    def calculate_county_customer_counts(self, prov_objects):
        """
        Calculate the counts from each provider for each county they cover and develop a county total.
        Gathers all county stats objects from all providers and sums the counts by county
        :param prov_objects: power provider objects
        :return: none
        """
        master_stat_obj_list = []
        county_objs = [obj for obj in prov_objects.values() if obj.style == DOIT_UTIL.COUNTY]
        for obj in county_objs:
            if obj.stats_objects is None:
                continue
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
        """
        Generate a sql statement for each county and the count and yield the statement for use in database transaction.
        :return: none
        """
        for obj in self.county_customer_count_objects_list:
            database_ready_area_name = obj.area.replace("'", "''")  # Prep apostrophe containing names for DB
            sql = self.sql_update_customer_counts_table.format(cust_count=obj.customers, area=database_ready_area_name)
            yield sql
