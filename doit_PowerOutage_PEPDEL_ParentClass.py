"""
Module contains a PEPDELParent class that inherits from Provider class. PEPDELParent class is an implementation
specific to the peculiarities of the DEL and PEP feeds and the processing they require that is not common to all
providers but common to them both. PEP and DEL had shared functionality. PEPDELParent was created as a result and is
intended to provide flexibility for future changes. It acts as an interface.
"""
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Outage
from PowerOutages_V2.doit_PowerOutage_ProviderClasses import Provider
import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS


class PEPDELParent(Provider):
    """
    Functionality and variables common to the PEP and DEL providers. Inherits from Provider. Portions are overridden
    in the PEP and DEL classes.
    """

    MULTI_ZIP_CODE_VALUE_DELIMITER = VARS.multi_zip_code_value_delimiter

    def __init__(self, provider_abbrev, style):
        super(PEPDELParent, self).__init__(provider_abbrev=provider_abbrev, style=style)
        self.area_list = None
        self.state_to_data_list_dict = None
        self.zip_desc_list = None

    def extract_areas_list_county(self):
        """
        Extract the county area information from a json response.
        :return: none
        """
        data_json = self.data_feed_response.json()
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json,
                                                          attribute_name="file_data")
        curr_custs_aff = DOIT_UTIL.extract_attribute_from_dict(data_dict=file_data,
                                                               attribute_name="curr_custs_aff")
        file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=curr_custs_aff,
                                                          attribute_name="areas")
        area_dict, *rest = file_data  # Expecting dict len=1, *rest guards against len>1
        self.area_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=area_dict,
                                                               attribute_name="areas")
        return

    def extract_county_outage_lists_by_state(self):
        """
        Extract county outage lists by state from dictionary
        :return: none
        """
        states_outages_list_dict = {}
        for state_dict in self.area_list:
            state_abbrev = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                 attribute_name="area_name")
            states_outages_list_dict[state_abbrev] = DOIT_UTIL.extract_attribute_from_dict(data_dict=state_dict,
                                                                                           attribute_name="areas")
        self.state_to_data_list_dict = states_outages_list_dict
        return

    def extract_outage_counts_by_county(self):
        """
        Extract outage counts by county from the outage dictionary, exchange state abbreviation for full name, and
        build stat objects
        :return: none
        """
        list_of_stats_objects = []
        for state_abbrev, outages_list in self.state_to_data_list_dict.items():
            state = DOIT_UTIL.exchange_state_abbrev_for_full_value(abbrev=state_abbrev)
            for county_dict in outages_list:
                county = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="area_name")
                outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict, attribute_name="custs_out")
                customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=county_dict,
                                                                  attribute_name="total_custs")
                list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                    style=self.style,
                                                    area=county,
                                                    outages=outages,
                                                    customers=customers,
                                                    state=state))
        self.stats_objects = list_of_stats_objects
        return

    def extract_zip_descriptions_list(self):
        """
        Extract zip descriptions list from response json
        :return: none
        """
        data_json = self.data_feed_response.json()
        self.zip_desc_list = DOIT_UTIL.extract_attribute_from_dict(data_dict=data_json, attribute_name="file_data")
        return

    def extract_outage_counts_by_zip_desc(self):
        """
        Extract the outage counts by zip and build stat objects
        :return: none
        """
        list_of_stats_objects = []
        for desc in self.zip_desc_list:
            zip_desc_dict, *rest = DOIT_UTIL.extract_attribute_from_dict(data_dict=desc, attribute_name="desc")
            zip_code = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="area_name")
            outages = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="custs_out")
            customers = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="total_custs")
            state_raw = DOIT_UTIL.extract_attribute_from_dict(data_dict=zip_desc_dict, attribute_name="state")
            state_groomed = DOIT_UTIL.exchange_state_abbrev_for_full_value(abbrev=state_raw)
            list_of_stats_objects.append(Outage(abbrev=self.abbrev,
                                                style=self.style,
                                                area=zip_code,
                                                outages=outages,
                                                customers=customers,
                                                state=state_groomed))
        self.stats_objects = list_of_stats_objects
        return

    def process_multi_value_zips_to_single_value(self):

        # Inspect every stat object
        stat_objs_to_delete = []
        new_stat_objs_to_append = []
        for stat_obj in self.stats_objects:

            # If the delimiter, currently a comma, is in the area then it is multi-value and needs to be processed
            if PEPDELParent.MULTI_ZIP_CODE_VALUE_DELIMITER in stat_obj.area:

                # Split the multi value string into singles and convert to type int
                singles = stat_obj.area.split(PEPDELParent.MULTI_ZIP_CODE_VALUE_DELIMITER)
            else:
                continue

            # For each single value, check if it is in the master maryland list of zips with geometry
            non_geometry_zips = []
            singles_geom_only = []
            for zipcode in singles:
                zipcode = zipcode.strip()

                # Check the master dictionary, try the key, if it's there it will work and if not it will throw
                try:

                    # if in dict then no error
                    _ = VARS.maryland_master_inventory_zip_codes_with_geometry[zipcode]
                except KeyError as ke:
                    non_geometry_zips.append(zipcode)
                    continue
                else:
                    singles_geom_only.append(zipcode)

            # Attempt to build stat objects for singles but protect against case where all singles are no-geometry zips
            if len(singles_geom_only) > 0:

                # Calculate the portion and the fraction of outages based on the number of singles remaining
                portion = stat_obj.outages // len(singles_geom_only)  # Truncation division
                fraction = stat_obj.outages % len(singles_geom_only)  # Finding remainder

                # Since this object will become new singles objects it now needs to be deleted from original list
                stat_objs_to_delete.append(stat_obj)

                # Create a list of the new singles objects that will be appended to the original list. Revise cust count
                singles_stats_objects_list = [Outage(abbrev=stat_obj.abbrev,
                                                     style=stat_obj.style,
                                                     area=value,    # NOTE
                                                     outages=portion,   # NOTE
                                                     customers=VARS.database_flag,  # NOTE
                                                     state=stat_obj.state
                                                     ) for value in singles_geom_only]

            else:
                print(f"WARNING: Multi-value zip string ({stat_obj.area}) (prov={stat_obj.abbrev}, state={stat_obj.state}) all registered as 'no-geometry' so count value ({stat_obj.outages}) could not be applied for MD map display.")
                continue

            # Apply the fraction until no more counts to distribute
            if fraction > 0:
                for old_obj in singles_stats_objects_list:
                    if fraction > 0:
                        old_obj.outages += 1
                        fraction -= 1

            print(f"Multi: {stat_obj}")
            for new_obj in singles_stats_objects_list:
                print(f"\tSingle: {new_obj}")

            # track old stats objects that have become new singles and new singles to be added to original list.
            new_stat_objs_to_append.extend(singles_stats_objects_list)

        # Delete old stats objects and add the new ones, from original list
        for old_obj in stat_objs_to_delete:
            self.stats_objects.remove(old_obj)
        self.stats_objects.extend(new_stat_objs_to_append)

        return
