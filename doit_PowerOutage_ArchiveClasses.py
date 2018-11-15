"""

"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class ArchiveCounty:
    def __init__(self):
        self.county_archive_record_objects_list = None
        self.sql_insert_record_county_archive = """INSERT INTO Archive_PowerOutagesCounty(STATE, COUNTY, Outage, updated, archived, percentage) VALUES ('{state}','{county}',{outage},'{updated}','{archived}','{percentage}')"""

    def build_list_of_archive_data_record_objects(self, selection):
        record_list = []
        for record in selection:
            record_obj = PowerOutagesViewForArchiveCountyData(*record)
            record_list.append(record_obj)
        self.county_archive_record_objects_list = record_list
        return

    def generate_county_archive_insert_sql_statement(self):
        for record_obj in self.county_archive_record_objects_list:
            record_obj.county = record_obj.county.replace("'", "''")  # Prepping county name values for re-entry into DB
            sql = self.sql_insert_record_county_archive.format(
                state=record_obj.state,
                county=record_obj.county,
                outage=record_obj.outage,
                updated=record_obj.updated,
                archived=record_obj.updated,
                percentage=round(record_obj.percentage, 3))
            yield sql


@dataclass
class PowerOutagesViewForArchiveCountyData:
    state: str
    county: str
    outage: int
    updated: datetime
    percentage: Decimal
