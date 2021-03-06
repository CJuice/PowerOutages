"""
Module contains a KubraParent class that inherits from Provider class. KubraParent class is an implementation
specific to the peculiarities of the DEL, PEP, and BGE feeds and the processing they require that is not common to all
providers but common to Kubra provided feeds. KubraParent was created as a result and is intended to provide
flexibility for future changes. It acts as an interface.
"""

from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages.doit_PowerOutage_ProviderClasses import Provider
import datetime
import pytz
import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS


class KubraParent(Provider):
    """
    Functionality and variables common to the Kubra feed (PEP, DEL, BGE) providers. Inherits from Provider.
    Certain functions are overloaded in child classes.
    """

    MULTI_ZIP_CODE_VALUE_DELIMITER = VARS.multi_zip_code_value_delimiter

    def __init__(self, provider_abbrev, style):
        super(KubraParent, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.area_list = None
        self.configuration_url = None
        self.configuration_feed_response = None
        self.date_created_attribute = "updatedAt"  # Attribute override from Provider
        self.kubra_data_dict_attribute = "data"
        self.instance_id = None
        self.interval_generation_data_attribute = "interval_generation_data"
        self.interval_generation_data = None
        self.metadata_key_attribute = "stormcenterDeploymentId"  # Attribute override from Provider
        self.view_id = None
        self.report_id = None
        self.report_source = None
        self.source_data_json = None
        self.source_report_json = None
        self.state_to_data_list_dict = None
        self.zip_desc_list = None

    def build_configuration_feed_uri(self) -> None:
        """
        Build the configuration feed uri by substituting the instance id, view id, and deployment id into the url
        :return: None
        """
        self.configuration_url = self.configuration_url.format(instance_id=self.instance_id, view_id=self.view_id,
                                                               deployment_id=self.metadata_key)
        return None

    def build_data_feed_uri(self) -> None:
        """
        Build the data feed uri by substituting the interval generation data value and source value into the url.
        Despite being called the 'data' feed and there being a kubra data.json available, this builds the string
        to access the report.json url.
        Override of Provider method.
        :return: None
        """
        self.data_feed_uri = self.data_feed_uri.format(interval_generation_data=self.interval_generation_data,
                                                       source=self.report_source)
        return None

    def extract_area_outage_lists_by_state(self) -> None:
        """
        Extract area outage lists by state from dictionary.
        :return: None
        """
        states_outages_list_dict = {}
        for state_dict in self.area_list:
            state_abbrev = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                 attribute_name="name")
            states_outages_list_dict[state_abbrev] = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                                           attribute_name="areas")
        self.state_to_data_list_dict = states_outages_list_dict
        return None

    def extract_outage_counts_by_area(self) -> None:
        """
        Extract outage counts by area from the outage dictionary, exchange state abbreviation for full name, and
        build stat objects
        :return: None
        """
        list_of_stats_objects = []
        for state_abbrev, outages_list in self.state_to_data_list_dict.items():
            state_groomed = DOIT_UTIL.exchange_state_abbrev_for_full_value(abbrev=state_abbrev)
            for area_dict in outages_list:
                area = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="name")
                outages_dict = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="cust_a")
                outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=outages_dict, attribute_name="val")
                customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict, attribute_name="cust_s")
                list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                    style=self.style,
                                                    area=area,
                                                    outages=outages,
                                                    customers=customers,
                                                    state=state_groomed))
        self.stats_objects = list_of_stats_objects
        return None

    def extract_source_report(self) -> None:
        """
        Extract the source report string value from the configuration feed response json
        :return: None
        """
        configuration_json = self.configuration_feed_response.json()
        config_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=configuration_json,
                                                            attribute_name="config")
        reports_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=config_data,
                                                             attribute_name="reports")
        data_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=reports_data,
                                                          attribute_name="data")
        interval_generation_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_data,
                                                                         attribute_name="interval_generation_data")
        county_data, zip_data, *rest = interval_generation_data  # expecting len 2, protect against more

        # Need to choose the correct data based on style of obj
        style_dict = {DOIT_UTIL.COUNTY: county_data, DOIT_UTIL.ZIP: zip_data}
        self.report_source = DOIT_UTIL.extract_attribute_from_dict(data_dict=style_dict.get(self.style),
                                                                   attribute_name="source")
        return None

    def extract_top_level_areas_list(self) -> None:
        """
        Extract the top level area key information from a json response.
        :return: None
        """
        data_json = self.data_feed_response.json()
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json,
                                                          attribute_name="file_data")
        self.area_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=file_data,
                                                               attribute_name="areas")
        return None

    def process_multi_value_zips_to_single_value(self) -> None:
        """
        Process "area" values, containing multiple comma separated zips, into new single zip value objects.
        This function is rather long and works on each stat object in a list at a time. The stat object .area attribute
        is examined, split into single values if necessary, then the .outages are divided evenly among the newly
        created single zip objects. The fractional remainder of outages are distributed evenly until there are no more
        outages to assign so that no values are created or lost. The original multi-value zip object is deleted from
        the stat objects list and the newly created single value zip objects are appended in their place. To give this
        process context, in the original process design the multi-value zips strings reported by PEP and DEL were
        written to the database as reported. Then, CTK zip values were checked against a database table that basically
        served as a dictionary. There was a single key value with a corresponding multi-value string of zips. The CTK
        single zips were converted to multi-value so that CTK, PEP, and DEL were all on the same page and mappable in
        an identical manner; CTK, PEP, and DEL had overlapping coverages and so their values needed to be standardized
        to be mappable. The new design does away with the multi-value method and simply breaks the multi into singles
        and distributes the counts as evenly as possible. This design is based around the zip code geometry layer
        instead of revolving around the business practice of PEP and DEL.
        :return: None
        """

        # Inspect every existing stat object to determine if it is multiple comma separated zips or a single zip
        stat_objs_to_delete = []    # Accumulate the multi zips that will be replaced by single
        new_stat_objs_to_append = []    # Accumulate the newly created single zip objects

        for stat_obj in self.stats_objects:

            # If the delimiter, currently a comma, is in the .area then it is multi-value and needs to be processed
            if KubraParent.MULTI_ZIP_CODE_VALUE_DELIMITER in stat_obj.area:

                # Split the multi value string into a list of single value zips
                singles = stat_obj.area.split(KubraParent.MULTI_ZIP_CODE_VALUE_DELIMITER)
            else:
                continue

            # For each single value, check if it is in the master maryland list of zips with geometry.
            # The master maryland list of zips with geometry came from a maryland zip codes feature class.
            non_geometry_zips = []
            geometry_zips = []

            for zipcode in singles:
                zipcode = zipcode.strip()

                # Check the master dictionary, try the key, if it's there it will work and if not it will throw
                try:

                    # TODO: Future, when incorporate point geometry zips will need to adjust here
                    # if in dict then no error, and we don't do anything with the area name value that is returned
                    _ = VARS.maryland_master_inventory_zip_codes_polygon_geometry[zipcode]

                except KeyError as ke:

                    # Accumulate the non-geometry zip codes
                    non_geometry_zips.append(zipcode)
                    continue

                else:

                    # Accumulate the zips that correspond with a valid zip polygon geometry.
                    geometry_zips.append(zipcode)

            # Attempt to build stat objects for singles but protect against case where all singles are non-geometry zips
            if len(geometry_zips) > 0:

                # Calculate the whole portion and the remaining fraction of outages based on the number of singles
                portion = stat_obj.outages // len(geometry_zips)  # Truncation division
                fraction = stat_obj.outages % len(geometry_zips)  # Finding remainder using modulo operator

                # Since the stat object of focus will be converted to new single zip value objects, it now needs to be
                #   deleted from the original list of stat objects. Accumulate those to be deleted.
                stat_objs_to_delete.append(stat_obj)

                # Create a list of the new singles objects that will be appended to the original list. Revise the
                #   customer count value because the original reported value will not be valid or used
                singles_stats_objects_list = [Outage(abbrev=stat_obj.abbrev,
                                                     style=stat_obj.style,
                                                     area=value,    # NOTICE
                                                     outages=portion,   # NOTICE
                                                     customers=VARS.database_flag,  # NOTICE
                                                     state=stat_obj.state
                                                     ) for value in geometry_zips]

            else:

                # The scenario, if encountered, where all zips in the multi-value string have no corresponding geometry.
                print(f"WARNING: Multi-value zip string ({stat_obj.area}) (prov={stat_obj.abbrev}, state={stat_obj.state}) all registered as 'no-geometry' so count value ({stat_obj.outages}) could not be applied for MD map display.")
                continue

            # Distribute the fraction amount until there are no more remainder outage counts
            if fraction > 0:
                for single_zip_obj in singles_stats_objects_list:
                    if fraction > 0:
                        single_zip_obj.outages += 1
                        fraction -= 1

            print(f"Multi-value zip: {stat_obj}")
            for single_zip_obj in singles_stats_objects_list:
                print(f"\tSingle: {single_zip_obj}")

            # Track new singles to be added to original list of stat objects.
            new_stat_objs_to_append.extend(singles_stats_objects_list)

        # Delete old stats objects
        for old_obj in stat_objs_to_delete:
            self.stats_objects.remove(old_obj)

        # Add the new single value objects to the original stat objects list
        self.stats_objects.extend(new_stat_objs_to_append)

        return None

    def process_date_created_to_seconds(self) -> None:
        """
        Process the Kubra date created milliseconds to a tz aware datetime obj and convert to formatted string.
        :return: None
        """
        seconds = self.date_created / 1000
        tz_eastern = pytz.timezone('US/Eastern')
        dt_obj = datetime.datetime.fromtimestamp(seconds, tz=tz_eastern)
        self.date_created = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")  # converted to string so dateutil.parser won't choke

        return None

