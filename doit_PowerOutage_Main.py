"""
This is a procedural script coordinating multiple imported classes to process power providers outage data for MEMA use.

The main() function contains all of the functionality. Imports include multiple custom modules that begin with
'doit_' to identify them as custom and not widely available python libraries. Main is generally organized into the
following order of sections: imports, variable definition/creation, web requests for various provider related data,
processing of response data, output of feed status to json file, and database transactions for 'realtime' and 'archive'
and customer data.
Main relies on the following imported modules containing classes: ArchiveClasses, CustomerClass,
CloudStorageFunctionality, CTKClasses, DatabaseFunctionality, DELClasses, EUCClasses, FESClasses, PEPClasses,
SMEClasses, and UtilityClass. It also relies on a CentralizedVariables python file,
and access through a parser to a Credentials config file and a ProvidersURI config file.
The process is designed with an object-oriented focus. For power providers, there is a top level parent class called
Provider. All providers are then subclassed from this parent to create child classes. The child classes contain
unique behavior specific to a provider. Functionality/behavior common to all providers has been placed into the parent
class and inherited downward into the children. For PEP DEL and BGE, Provider is inherited by the Kubra Parent Class.
This class organizes behavior common to those providers. The children inherit from
the Kubra parent, which inherits from Provider. Where necessary, some methods in parent classes have been overloaded
by methods in child classes.
A Utility class is used by all modules and serves as a static resource for common/shared helper functions and a few
simple variables. The Centralized Variables module contains variables, no classes or functions, and environment related
variables and sql statements. It is not intended to be used by Utility class.
A Web Related Functionality class exists for web related functionality and is accessed by the Provider exclusively.
The output json file named PowerOutageFeeds_StatusJSON.json is stored in a folder named JSON_Outputs.
Author: CJuice
Revisions:
20190327, CJuice Redesign for change to SME data feeds
20200430, CJuice Revised code to check for None in critical objects. Spawned from PEP and DEL feeds being down.
    Entire process failed. Now handles None. Notification email alerts were also modified to send fewer per provider.
    Deployed application currently sends emails to CJuice for Dev and Prod. Prod to be corrected to mjoc after redesign
    for revised feeds happens. Customer Class and Provider Class were revised to include None checks to avoid failure
20200512, CJuice Redesigned for new Kubra based feeds for PEP and DEL after the old feeds were turned off.
    Heavily revised Main, PEPDEL_ParentClass, PEPClasses, DELClasses ProviderURI, and did minor alterations to other
    classes for clarity or minor improvements in documentation or style but not functionality.
20200520, CJuice Revised PEPCO zip code harvesting after discovering issues with Exelon zip code values
    that were provided to us. Switched to identifying MD zip codes first using geometry zip list, then identifying DC
    zips based on web scraped usps zip code list, and finally printing out message on unknown zips but with no
    other action. Refactored code to reduce nested code where could. Did discover two valid zip codes that are missing
    from MDP sourced zip code spatial layer behind master MD zip codes list. Contacted MDP, said to be adding soon
    and will provide update. Process could be improved with those MD zips added.
20201110, CJuice Redesigned process for change to BGE feed. BGE feed now coming from Kubra. Added a cloud functionality
    class for upsert of data to our open data portal, currently Socrata. Three datasets are updserted and those are
    county, zip code, and feed status. Implemented processing and upsert at the very end so that if it were to fail
    it would not interfere with the existing MEMA database functionality.
20210330, CJuice Redesigned to move data storage model to be cloud based. Added Socrata and ESRI ArcGIS Online
    upsert functionality.
20210401, CJuice Added Open Data record deletion functionality for cleanup of records older than set limit
20210430, CJuice Added purge of zip code stats objects not in the Maryland point and polygon zip code inventory based
    on the MDP point and polygon spatial layer features.
"""


def main():

    # IMPORTS
    from PowerOutages.doit_PowerOutage_ArchiveClasses import ArchiveCounty
    from PowerOutages.doit_PowerOutage_ArchiveClasses import ArchiveZIP
    from PowerOutages.doit_PowerOutage_CloudStorageFunctionality import ArcGISOnline
    from PowerOutages.doit_PowerOutage_CloudStorageFunctionality import CloudStorage
    from PowerOutages.doit_PowerOutage_CloudStorageFunctionality import OpenData
    from PowerOutages.doit_PowerOutage_UtilityClass import Utility as DOIT_UTIL
    from PowerOutages.doit_PowerOutage_ArchiveClasses import ZipCodeCountAggregated

    import PowerOutages.doit_PowerOutage_BGEClasses as BGEMod
    import PowerOutages.doit_PowerOutage_CustomerClass as Customer
    import PowerOutages.doit_PowerOutage_CTKClasses as CTKMod
    import PowerOutages.doit_PowerOutage_DatabaseFunctionality as DbMod
    import PowerOutages.doit_PowerOutage_DELClasses as DELMod
    import PowerOutages.doit_PowerOutage_EUCClasses as EUCMod
    import PowerOutages.doit_PowerOutage_FESClasses as FESMod
    import PowerOutages.doit_PowerOutage_PEPClasses as PEPMod
    import PowerOutages.doit_PowerOutage_SMEClasses as SMEMod
    import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS

    import os

    print(f"Initiated process @ {DOIT_UTIL.current_date_time_str()}")

    # VARIABLES
    provider_uri_cfg_path = os.path.join(VARS._root_project_path, VARS.provider_uri_cfg_file)
    credentials_cfg_path = os.path.join(VARS._root_project_path, VARS.credentials_cfg_file)
    DOIT_UTIL.PARSER.read(filenames=[credentials_cfg_path, provider_uri_cfg_path])
    output_json_file = os.path.join(VARS._root_project_path, VARS.json_file_local_location_and_name)

    #   Set up provider objects for use. Later referred to as "key, obj" in iteration loops.
    provider_objects = {"BGE_County": BGEMod.BGE(provider_abbrev="BGE", style=DOIT_UTIL.COUNTY),
                        "BGE_ZIP": BGEMod.BGE(provider_abbrev="BGE", style=DOIT_UTIL.ZIP),
                        "CTK_County": CTKMod.CTK(provider_abbrev="CTK", style=DOIT_UTIL.COUNTY),
                        "CTK_ZIP": CTKMod.CTK(provider_abbrev="CTK", style=DOIT_UTIL.ZIP),
                        "DEL_County": DELMod.DEL(provider_abbrev="DEL", style=DOIT_UTIL.COUNTY),
                        "DEL_ZIP": DELMod.DEL(provider_abbrev="DEL", style=DOIT_UTIL.ZIP),
                        "EUC_County": EUCMod.EUC(provider_abbrev="EUC", style=DOIT_UTIL.COUNTY),
                        "EUC_ZIP": EUCMod.EUC(provider_abbrev="EUC", style=DOIT_UTIL.ZIP),
                        "FES_County": FESMod.FES(provider_abbrev="FES", style=DOIT_UTIL.COUNTY),
                        "FES_ZIP": FESMod.FES(provider_abbrev="FES", style=DOIT_UTIL.ZIP),
                        "PEP_County": PEPMod.PEP(provider_abbrev="PEP", style=DOIT_UTIL.COUNTY),
                        "PEP_ZIP": PEPMod.PEP(provider_abbrev="PEP", style=DOIT_UTIL.ZIP),
                        "SME_County": SMEMod.SME(provider_abbrev="SME", style=DOIT_UTIL.COUNTY),
                        "SME_ZIP": SMEMod.SME(provider_abbrev="SME", style=DOIT_UTIL.ZIP),
                        }

    #   Get and store variables, as provider object attributes, from cfg file.
    print(f"Gathering variables...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        section_keys = [item for item in DOIT_UTIL.PARSER[key]]
        section_values = [DOIT_UTIL.PARSER[key][section_key] for section_key in section_keys]
        if obj.abbrev in VARS.kubra_feed_providers:

            # 20201014 CJuice Redesign to include use of report_id for all Kubra, following use of report_id in BGE flow.
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_feed_uri, obj.configuration_url, obj.instance_id, obj.view_id, obj.report_id = section_values
        else:
            obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_feed_uri = section_values

    # WEB REQUESTS AND PROCESSING OF RESPONSE CONTENT
    #   Make the metadata key requests, for those providers that use the metadata key, and store the response.
    #   Key used in the uri for accessing the data feeds and date created feeds.
    print(f"Metadata feed processing...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.metadata_feed_uri in VARS.none_and_not_available:

            # Providers who do not use the metadata key style.
            continue
        else:
            obj.metadata_feed_response = obj.web_func_class.make_web_request(uri=obj.metadata_feed_uri)

    #   Extract the metadata key and assign to provider object attribute for later use.
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.metadata_feed_uri in VARS.none_and_not_available:
            continue
        else:
            if "xml" in obj.metadata_feed_response.headers["content-type"]:
                metadata_xml_element = DOIT_UTIL.parse_xml_response_to_element(
                    response_xml_str=obj.metadata_feed_response.text)
                obj.metadata_key = DOIT_UTIL.extract_attribute_value_from_xml_element_by_index(
                    root_element=metadata_xml_element)
            else:
                metadata_response_dict = obj.metadata_feed_response.json()
                obj.metadata_key = DOIT_UTIL.extract_attribute_from_dict(
                    data_dict=metadata_response_dict,
                    attribute_name=obj.metadata_key_attribute)

        # Kubra specific, there is a second key needed
        if obj.abbrev in VARS.kubra_feed_providers:
            metadata_response_dict = obj.metadata_feed_response.json()
            interval_gen_data_dict = DOIT_UTIL.extract_attribute_from_dict(
                data_dict=metadata_response_dict,
                attribute_name=obj.kubra_data_dict_attribute)
            obj.interval_generation_data = DOIT_UTIL.extract_attribute_from_dict(
                data_dict=interval_gen_data_dict,
                attribute_name=obj.interval_generation_data_attribute)

    #   Make the date created requests, for providers with a date created service, and store the response.
    #   NOTE: For Kubra feeds this is a second call to the metadata key uri (above)
    print(f"Date Generated feed processing...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.date_created_feed_uri in VARS.none_and_not_available:
            continue
        else:
            obj.date_created_feed_uri = DOIT_UTIL.build_feed_uri(metadata_key=obj.metadata_key,
                                                                 data_feed_uri=obj.date_created_feed_uri)
            obj.date_created_feed_response = obj.web_func_class.make_web_request(uri=obj.date_created_feed_uri)

    #   Extract the date created value and assign to provider object attribute
    print(f"Extracting date created value...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.date_created_feed_uri in VARS.none_and_not_available:
            continue
        else:
            if "xml" in obj.date_created_feed_response.headers["content-type"]:
                date_created_xml_element = DOIT_UTIL.parse_xml_response_to_element(
                    response_xml_str=obj.date_created_feed_response.text)
                obj.date_created = DOIT_UTIL.extract_attribute_value_from_xml_element_by_index(
                    root_element=date_created_xml_element)
            else:
                date_created_response_dict = obj.date_created_feed_response.json()

                # Kubra specific, date data sits at different levels of response json
                if obj.abbrev in VARS.kubra_feed_providers:
                    obj.date_created = DOIT_UTIL.extract_attribute_from_dict(
                        data_dict=date_created_response_dict,
                        attribute_name=obj.date_created_attribute)

                    # Kubra datetime requires processing to match format of other providers dt strings
                    obj.process_date_created_to_seconds()
                else:
                    file_data = DOIT_UTIL.extract_attribute_from_dict(data_dict=date_created_response_dict,
                                                                      attribute_name=obj.file_data_attribute)
                    obj.date_created = DOIT_UTIL.extract_attribute_from_dict(
                        data_dict=file_data,
                        attribute_name=obj.date_created_attribute)

    print(f"Configuration feed processing (Kubra)...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        if obj.abbrev in VARS.kubra_feed_providers:
            DOIT_UTIL.print_tabbed_string(value=key)
            obj.build_configuration_feed_uri()
            obj.configuration_feed_response = obj.web_func_class.make_web_request(uri=obj.configuration_url)
            obj.extract_source_report()

    #   Make the data feed requests and store the response.
    print(f"Data feed requests and response storage...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.metadata_key in VARS.none_and_not_available:
            obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)
        else:
            obj.build_data_feed_uri()
            obj.data_feed_response = obj.web_func_class.make_web_request(uri=obj.data_feed_uri)

    # PROCESS RESPONSE DATA
    #   Extract the outage data from the response, for each provider. Where applicable, extract the
    #   date created/generated. Some providers provide the date created/generated value in the data feed.
    print(f"Response data processing...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.data_feed_response.status_code != 200:
            print(f"Data feed response status code != 200: {key} {obj.data_feed_response.status_code}")
            continue

        if key in ("FES_County", "FES_ZIP"):
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_area_outage_elements()
            obj.extract_outage_counts()
            obj.create_stats_objects()
            obj.extract_date_created()

        elif key in ("DEL_County", "PEP_County", "BGE_County"):
            obj.extract_top_level_areas_list()
            obj.extract_area_outage_lists_by_state()
            obj.extract_outage_counts_by_area()

        elif key in ("DEL_ZIP", "PEP_ZIP", "BGE_ZIP"):
            obj.extract_top_level_areas_list()
            obj.extract_area_outage_lists_by_state()
            obj.extract_outage_counts_by_area()
            obj.process_multi_value_zips_to_single_value()

        elif key in ("SME_County", "SME_ZIP"):
            obj.extract_areas_list()
            obj.extract_outage_counts()

        elif key in ("EUC_County", "EUC_ZIP"):
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_outage_events_list_from_xml_str()
            obj.extract_outage_counts()
            obj.extract_date_created()

        elif key in ("CTK_County", "CTK_ZIP"):
            obj.xml_element = DOIT_UTIL.parse_xml_response_to_element(response_xml_str=obj.data_feed_response.text)
            obj.extract_report_by_id()
            obj.extract_outage_dataset()
            obj.extract_outage_counts_from_dataset()
            obj.extract_date_created()

        # Need to remove duplicates, isolate MD zips, correct spelling & punctuation, convert str counts to int,
        #   and process date/time
        obj.purge_duplicate_stats_objects()
        obj.purge_zero_outage_zip_stats_objects()
        obj.remove_non_maryland_stat_objects()
        DOIT_UTIL.revise_county_name_spellings_and_punctuation(stats_objects_list=obj.stats_objects)
        DOIT_UTIL.remove_commas_from_counts(objects_list=obj.stats_objects)
        DOIT_UTIL.process_stats_objects_counts_to_integers(objects_list=obj.stats_objects, keyword="customers")
        DOIT_UTIL.process_stats_objects_counts_to_integers(objects_list=obj.stats_objects, keyword="outages")
        obj.groom_date_created()
        obj.calculate_data_age_minutes()

    # JSON FILE OUTPUT AND FEED STATUS EVALUATION
    #   Write json file containing status check on all feeds.
    print(f"Checking feed status's for notification purposes...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        obj.set_status_codes()

        #   Down Feeds - Send Notification Email to MJOC. Piggy back on JSON feed status process
        obj.perform_feed_status_check_and_notification(alert_email_address=DOIT_UTIL.PARSER["EMAIL"]["ALERTS_ADDRESS"])

    print(f"Writing feed check to json file...{DOIT_UTIL.current_date_time_str()}")
    status_check_output_dict = {}
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        status_check_output_dict.update(obj.build_output_dict(unique_key=key))
    DOIT_UTIL.write_to_file(file=output_json_file, content=status_check_output_dict)

    # DATABASE TRANSACTIONS
    #   Prepare for database transactions and establish a connection.
    print(f"Database operations initiated...{DOIT_UTIL.current_date_time_str()}")
    db_obj = DbMod.DatabaseUtilities(parser=DOIT_UTIL.PARSER)
    db_obj.create_database_connection_string()
    db_obj.establish_database_connection()

    # REALTIME: For every provider object need to delete existing records, and update with new. Need a cursor to do so.
    db_obj.create_database_cursor()
    print(f"RealTime counts update process initiated...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)

        # Need to delete existing records from database table for every/all provider. All the same WRT delete.
        db_obj.delete_records(style=obj.style, provider_abbrev=obj.abbrev)

        try:
            realtime_insert_generator = obj.generate_insert_sql_statement_realtime()
            for sql_statement in realtime_insert_generator:
                db_obj.execute_sql_statement(sql_statement=sql_statement)
        except TypeError as te:
            print(f"TypeError. REALTIME process. {obj.abbrev} appears to have no stats objects. \n{te}")
        else:
            db_obj.commit_changes()
            print(f"Records inserted ({DOIT_UTIL.current_date_time_str()}): {obj.abbrev}  {obj.style} {len(obj.stats_objects)}")

    # Clean up for next step
    db_obj.delete_cursor()

    # CUSTOMER COUNT: Before moving to archive stage, where customer count is used to calculate percent outage, update
    #   the customer counts table using data feed values.
    print(f"County customer counts update process initiated...{DOIT_UTIL.current_date_time_str()}")
    db_obj.create_database_cursor()
    cust_obj = Customer.Customer()
    cust_obj.calculate_county_customer_counts(prov_objects=provider_objects)
    customer_count_update_generator = cust_obj.generate_insert_sql_statement_customer_count()
    try:
        for statement in customer_count_update_generator:
            db_obj.execute_sql_statement(sql_statement=statement)
    except Exception as e:
        # TODO: Refine exception handling when determine what issue types could be
        print(f"CUSTOMER COUNT process. Database operation error. {e}")
    db_obj.commit_changes()

    # Clean up for next step
    db_obj.delete_cursor()

    # ARCHIVE STEPS
    # ZIP: SUM outage counts by Zip. Append aggregated count records to the Archive_PowerOutagesZipcode table.
    print(f"Archive counts update process initiated...{DOIT_UTIL.current_date_time_str()}")
    archive_zip_obj = ArchiveZIP()
    db_obj.create_database_cursor()

    # Aggregate counts for all zips from all providers to account for outages for zips covered by multiple providers
    print(f"Zip Code outage counts aggregation initiated...{DOIT_UTIL.current_date_time_str()}")
    for key, obj in provider_objects.items():
        DOIT_UTIL.print_tabbed_string(value=key)
        if obj.style == DOIT_UTIL.COUNTY:
            continue
        if obj.stats_objects in VARS.none_and_not_available:
            continue

        for stat_obj in obj.stats_objects:
            try:

                # if exists already, add outages and revise provider abbreviation to indicate multiple ('MULTI')
                archive_zip_obj.master_aggregated_zip_count_objects_dict[stat_obj.area].outages += stat_obj.outages
                archive_zip_obj.master_aggregated_zip_count_objects_dict[stat_obj.area].abbrev = VARS.multiple_providers
            except KeyError as ke:

                # Zip key does not exist already so add zip key to dictionary and store dataclass object as value
                archive_zip_obj.master_aggregated_zip_count_objects_dict[stat_obj.area] = ZipCodeCountAggregated(
                    area=stat_obj.area,
                    abbrev=stat_obj.abbrev,
                    outages=stat_obj.outages,
                    date_created=obj.date_created,
                    date_updated=obj.date_updated)

    # Insertion into Archive_PowerOutagesZipcode
    try:
        zip_archive_insert_generator = archive_zip_obj.generate_insert_sql_statement_archive()
        for sql_statement in zip_archive_insert_generator:
            db_obj.execute_sql_statement(sql_statement=sql_statement)
    except Exception as e:
        print(f"ARCHIVE ZIP process. Database insertion operation error. {e}")
        exit()
    else:
        db_obj.commit_changes()
        print(f"{len(archive_zip_obj.master_aggregated_zip_count_objects_dict.values())} ZIP archive records inserted into Archive_PowerOutagesZipcode...{DOIT_UTIL.current_date_time_str()}")

    # Clean up for next step
    db_obj.delete_cursor()

    # TODO: Reassess. Why is this happening? Is this transaction necessary?
    # COUNTY: Get selection from PowerOutages_PowerOutagesViewForArchive and write to Archive_PowerOutagesCounty
    #   Selection from PowerOutages_PowerOutagesViewForArchive, all fields except geometry, for insertion
    archive_county_obj = ArchiveCounty()
    try:
        db_obj.create_database_cursor()
        db_obj.execute_sql_statement(sql_statement=VARS.sql_select_counties_viewforarchive)
        db_obj.fetch_all_from_selection()
    except Exception as e:
        # TODO: Refine exception handling when determine what issue types could be
        print(f"ARCHIVE County process. Database selection operation error. {e}")
        exit()
    else:
        archive_county_obj.build_list_of_archive_data_record_objects(selection=db_obj.selection)
    finally:

        # Clean up for next step
        db_obj.delete_cursor()

    #   Insertion into Archive_PowerOutagesCounty
    try:
        db_obj.create_database_cursor()
        county_archive_insert_generator = archive_county_obj.generate_county_archive_insert_sql_statement()
        for sql_statement in county_archive_insert_generator:
            db_obj.execute_sql_statement(sql_statement=sql_statement)
    except Exception as e:
        # TODO: Refine exception handling when determine what issue types could be
        print(f"ARCHIVE County process. Database insertion operation error. {e}")
        print(e)
        exit()
    else:
        db_obj.commit_changes()
        print(f"{len(archive_county_obj.county_archive_record_objects_list)} County archive records inserted into Archive_PowerOutagesCounty...{DOIT_UTIL.current_date_time_str()}")
    finally:

        # Clean up for next step
        db_obj.delete_cursor()

    #   Update RealTime_TaskTracking
    try:
        db_obj.create_database_cursor()
        sql_task_tracking_update = VARS.sql_update_task_tracking_table.format(now=DOIT_UTIL.current_date_time_str())
        db_obj.execute_sql_statement(sql_statement=sql_task_tracking_update)
    except Exception as e:
        print(f"Task Tracking update. Database insertion operation error. {e}")
        print(e)
        exit()
    else:
        db_obj.commit_changes()
        print(f"Task Tracking table updated...{DOIT_UTIL.current_date_time_str()}")
    finally:

        # Clean up for next step
        db_obj.delete_cursor()

    # CLOUD STORAGE
    print(f"Processing data for cloud storage...{DOIT_UTIL.current_date_time_str()}")

    # Generic processing, not specific to County or ZIP Code
    cloud_storage = CloudStorage()
    cloud_storage.create_outage_records(provider_objects=provider_objects)
    cloud_storage.create_master_outage_dataframe()
    cloud_storage.group_by_area()
    cloud_storage.sum_outages()
    cloud_storage.create_unique_id_outages()
    cloud_storage.create_dt_stamp_column(dataframe=cloud_storage.grouped_sums_df)

    # Data separated by area type (County vs ZIP)
    cloud_storage.isolate_county_style_records()
    cloud_storage.isolate_zip_style_records()
    cloud_storage.calculate_county_outage_percentage()
    cloud_storage.drop_customers_from_zip_df()
    CloudStorage.drop_style_from_record_dfs(data_dataframe=cloud_storage.county_outage_records_df)
    CloudStorage.drop_style_from_record_dfs(data_dataframe=cloud_storage.zipcode_outage_records_df)

    # Feed Status Data
    cloud_storage.create_feed_status_dataframe(status_check_output=status_check_output_dict)
    cloud_storage.correct_status_created_dt()
    cloud_storage.create_unique_id_feed_status()
    cloud_storage.create_dt_stamp_column(dataframe=cloud_storage.feed_status_df)
    cloud_storage.correct_data_age_field_name()

    # Prepare the three data realms for upsert to open data platform
    cloud_storage.county_zipper = CloudStorage.create_lists_of_record_dicts(dataframe=cloud_storage.county_outage_records_df)
    cloud_storage.zipcode_zipper = CloudStorage.create_lists_of_record_dicts(dataframe=cloud_storage.zipcode_outage_records_df)
    cloud_storage.feed_status_zipper = CloudStorage.create_lists_of_record_dicts(dataframe=cloud_storage.feed_status_df)

    print(f"Upserting data to cloud storage...{DOIT_UTIL.current_date_time_str()}")
    print("OPEN DATA PORTAL")
    open_data = OpenData(parser=DOIT_UTIL.PARSER)
    open_data.create_socrata_client()

    print("Upsert Results: County, ZIP, Feed Status...")
    open_data.upsert_to_socrata(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["COUNTY_4X4"],
                                zipper=cloud_storage.county_zipper)
    open_data.upsert_to_socrata(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["ZIP_4X4"],
                                zipper=cloud_storage.zipcode_zipper)
    open_data.upsert_to_socrata(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["STATUS_4X4"],
                                zipper=cloud_storage.feed_status_zipper)

    print("ARCGIS ONLINE")
    gis_connection = ArcGISOnline.create_gis_connection()
    agol_style_to_df_dict = {
        DOIT_UTIL.COUNTY: cloud_storage.county_outage_records_df,
        DOIT_UTIL.ZIP: cloud_storage.zipcode_outage_records_df
    }

    for style_type, style_df in agol_style_to_df_dict.items():
        print(style_type)
        arc_cloud_obj = ArcGISOnline(parser=DOIT_UTIL.PARSER, style=style_type, gis_connection=gis_connection,
                                     data_df=style_df)
        arc_cloud_obj.drop_unnecessary_fields()
        arc_cloud_obj.localize_dt_values()
        arc_cloud_obj.csv_item = arc_cloud_obj.get_arcgis_item(item_id=arc_cloud_obj.csv_item_id)
        arc_cloud_obj.write_temp_csv()
        arc_cloud_obj.update_csv_item()
        arc_cloud_obj.hosted_table_item = arc_cloud_obj.get_arcgis_item(item_id=arc_cloud_obj.hosted_table_item_id)
        arc_cloud_obj.create_arcgis_features_table()
        arc_cloud_obj.analyze_table()
        arc_cloud_obj.delete_features()
        arc_cloud_obj.append_new_outage_data()

    print(f"Deleting aged records ({OpenData.RECORD_DELETION_AGE_LIMIT_DAYS} days) in Open Data assets...{DOIT_UTIL.current_date_time_str()}")
    county_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["COUNTY_4X4"])
    zip_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["ZIP_4X4"])
    status_records_gen = open_data.retrieve_old_records_for_deletion(
        dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["STATUS_4X4"])

    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["COUNTY_4X4"],
                                    results_gen=county_records_gen)
    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["ZIP_4X4"],
                                    results_gen=zip_records_gen)
    open_data.delete_records_by_uid(dataset_identifier=DOIT_UTIL.PARSER["OPENDATA"]["STATUS_4X4"],
                                    results_gen=status_records_gen)

    print(f"Process Completed...{DOIT_UTIL.current_date_time_str()}")


if __name__ == "__main__":
    main()

