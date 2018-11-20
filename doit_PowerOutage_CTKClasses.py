"""

"""
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS


class CTK(Provider):

    SQL_SELECT_GROUPED_ZIPCODES = VARS.sql_select_grouped_zipcodes

    def __init__(self, provider_abbrev, style):
        super().__init__(provider_abbrev=provider_abbrev, style=style)
        self.xml_element = None
        self.outage_report = None
        self.outage_dataset = None
        self.grouped_zipcodes_dict = None

    def extract_date_created(self):
        date_generated = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=self.xml_element,
                                                                                      tag_name="generated")
        date_dict = date_generated.attrib
        self.date_created = DOIT_UTIL.extract_attribute_from_dict(data_dict=date_dict, attribute_name="date")
        return

    def extract_report_by_id(self):
        style_id = self.style
        for report in self.xml_element.iter("report"):
            if report.attrib["id"].lower() == style_id.lower():
                self.outage_report = report
                return

    def extract_outage_dataset(self):
        self.outage_dataset = DOIT_UTIL.extract_first_immediate_child_feature_from_element(element=self.outage_report,
                                                                                           tag_name="dataset")
        if len(self.outage_dataset) == 0:
            print(f"No {self.abbrev}_{self.style} dataset values in feed.\nResponse value: {self.data_feed_response}")
        return

    def extract_outage_counts_from_dataset(self):
        list_of_stats_objects = []
        t_elements = DOIT_UTIL.extract_all_immediate_child_features_from_element(element=self.outage_dataset,
                                                                                 tag_name="t")
        area_index, customers_index, affected_index = (0, 1, 2)
        for t in t_elements:
            e_list = DOIT_UTIL.extract_all_immediate_child_features_from_element(element=t, tag_name="e")
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=e_list[area_index].text,
                                                outages=e_list[affected_index].text,
                                                customers=e_list[customers_index].text,
                                                state=DOIT_UTIL.MARYLAND))
        self.stats_objects = list_of_stats_objects
        return

    def create_grouped_zipcodes_dict(self, cursor):
        record_dict = {}
        for record in cursor.execute(CTK.SQL_SELECT_GROUPED_ZIPCODES):
            single_zip, zip_id = record
            record_dict[single_zip] = zip_id
        self.grouped_zipcodes_dict = record_dict
        return

    def generate_insert_sql_statement_realtime(self):
        self.date_updated = DOIT_UTIL.current_date_time()
        for stat_obj in self.stats_objects:
            if self.style == "ZIP":
                area_of_focus = stat_obj.area
                try:
                    area_value = self.grouped_zipcodes_dict[area_of_focus]
                except KeyError as ke:
                    area_value = area_of_focus
                sql = self.sql_insert_record_zip_realtime.format(area=area_value,
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