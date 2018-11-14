"""

"""
from PowerOutages_V2.doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL


class DEL(PEPDELParent):

    SPECIAL_ZIP_VALUES_DICT = {"21921,21922": "21916,21920,21921"}

    def __init__(self, provider_abbrev, style):
        super(DEL, self).__init__(provider_abbrev=provider_abbrev, style=style)

    def generate_insert_sql_statement_realtime(self):
        self.date_updated = DOIT_UTIL.current_date_time()
        for stat_obj in self.stats_objects:
            if self.style == "ZIP":
                try:
                    stat_obj.area = DEL.SPECIAL_ZIP_VALUES_DICT[stat_obj.area]
                except KeyError as ke:
                    pass
                sql = self.sql_insert_record_zip_realtime.format(area=stat_obj.area,
                                                                 abbrev=stat_obj.abbrev,
                                                                 outages=stat_obj.outages,
                                                                 date_created=self.date_created,
                                                                 date_updated=self.date_updated
                                                                 )
            else:
                sql = self.sql_insert_record_county_realtime.format(state=stat_obj.state,
                                                                    county=stat_obj.area,
                                                                    outages=stat_obj.outages,
                                                                    abbrev=self.abbrev,
                                                                    date_updated=self.date_updated,
                                                                    date_created=self.date_created
                                                                    )
            yield sql