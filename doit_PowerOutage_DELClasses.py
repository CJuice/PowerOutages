"""
Module contains a DEL class that inherits from PEPDELParent class which inherits from Provider class. 
DEL class is an implementation specific to the peculiarities of the DEL feeds and the processing they require
that is not common to all providers. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface. DEL inherits from the PEPDELParent class.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_PEPDEL_ParentClass import PEPDELParent


class DEL(PEPDELParent):
    """
    DEL specific functionality and variables for handling DEL feed data. Inherits from PEPDELParent and therefore
    Provider. DEL has unique requirements related to zip codes.
    """

    def __init__(self, provider_abbrev, style):
        super(DEL, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.SPECIAL_ZIP_VALUES_DICT = {"21921,21922": "21916,21920,21921"}

    def generate_insert_sql_statement_realtime(self):
        """
        Generate insert sql statements and yield the string.
        Overrides method in Provider. Contains one bit of unique functionality that offsets it from the Provider method 
        that it overrides. The stat obj area, if the style is ZIP, must be checked against the special zip code values
        dictionary before the insert sql statement is built.  
        :return: none 
        """
        self.date_updated = DOIT_UTIL.current_date_time()
        for stat_obj in self.stats_objects:
            if self.style == "ZIP":
                try:
                    stat_obj.area = self.SPECIAL_ZIP_VALUES_DICT[stat_obj.area]
                except KeyError as ke:
                    pass
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