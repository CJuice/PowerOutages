import textwrap

credentials_cfg_file = "doit_PowerOutage_Credentials.cfg"
database_connection_string = "DSN={database_name};UID={database_user};PWD={database_password}"
json_file_local_location_and_name = "JSON_Outputs\PowerOutageFeeds_StatusJSON.json"
less_than_five = "Less than 5"
provider_uri_cfg_file = "doit_PowerOutage_ProviderURI.cfg"
sme_customer_count_database_location_and_name = "SME_Customer_Count_Memory_DB\SME_Customer_Count_Memory_DB.db"
sme_database_table_name = "SME_Customer_Count_Memory"
sql_create_county_table_sme_sqlite3 = textwrap.dedent(
    """CREATE TABLE :table_name (
        County_ID integer primary key autoincrement, 
        County_Name text, 
        Customer_Count integer, 
        Last_Updated text
    )"""
)
sql_delete_statement = textwrap.dedent(
    """DELETE FROM RealTime_PowerOutages{style} 
    WHERE PROVIDER = '{provider_abbrev}'"""
)
sql_insert_into_county_table_sme_sqlite3 = textwrap.dedent(
    """INSERT INTO :table_name VALUES (
        Null,
        :county_name, 
        :cust_count, 
        :date_updated
    )"""
)
sql_insert_record_county_archive = textwrap.dedent(
    """INSERT INTO Archive_PowerOutagesCounty(
            STATE, 
            COUNTY, 
            Outage, 
            updated, 
            archived, 
            percentage
        ) 
        VALUES (
            '{state}',
            '{county}',
            {outage},
            '{updated}',
            '{archived}',
            '{percentage}'
        )"""
)
sql_insert_record_county_realtime = textwrap.dedent(
    """INSERT INTO dbo.RealTime_PowerOutagesCounty(
            STATE, 
            COUNTY, 
            OUTAGE, 
            PROVIDER, 
            UPDATED, 
            CREATED
        ) 
        VALUES (
            '{state}',
            '{county}',
            {outages},
            '{abbrev}',
            '{date_updated}',
            '{date_created}'
        )"""
)
sql_insert_record_zip_archive = textwrap.dedent(
    """INSERT INTO dbo.Archive_PowerOutagesZipcode(
            ZIPCODE,
            ID, 
            PROVIDER, 
            OUTAGE, 
            CREATED, 
            UPDATED, 
            ARCHIVED
        ) 
        VALUES (
            '{area}',
            'NULL',
            '{abbrev}',
            {outages},
            '{date_created}',
            '{date_updated}',
            '{date_updated}'
        )"""
)
sql_insert_record_zip_realtime = textwrap.dedent(
    """INSERT INTO dbo.RealTime_PowerOutagesZipcodes(
            ZIPCODE, 
            PROVIDER, 
            OUTAGE, 
            CREATED, 
            UPDATED
        ) 
        VALUES (
            '{area}',
            '{abbrev}',
            {outages},
            '{date_created}',
            '{date_updated}'
        )"""
)
sql_select_by_provider_abbrev_realtime = textwrap.dedent(
    """SELECT {fields} FROM dbo.RealTime_PowerOutages{style}
    WHERE PROVIDER = '{provider_abbrev}'"""
)
sql_select_counties_viewforarchive = textwrap.dedent(
    """SELECT state, county, outage, updated, percentage 
    FROM OSPREYDB_DEV.dbo.PowerOutages_PowerOutagesViewForArchive 
    WHERE state is not Null"""
)
sql_select_county_data_sme_sqlite3 = textwrap.dedent(
    """SELECT County_ID, County_Name, Customer_Count 
    FROM SME_Customer_Count_Memory"""
)
# TODO: replace * with field names to avoid errors in future if fields are added etc. Be specific in selection!
sql_select_grouped_zipcodes = textwrap.dedent(
    """SELECT * 
    FROM dbo.RealTime_PowerOutagesZipcodes_Grouped"""
)
sql_select_zip_by_provider_abbrev_realtime = textwrap.dedent(
    """SELECT zipcode FROM dbo.RealTime_PowerOutagesZipcodes 
    WHERE PROVIDER = '{provider_abbrev}'"""
)
sql_update_customer_counts_table = textwrap.dedent(
    """UPDATE dbo.RealTime_PowerOutagesCounty_Customers 
    SET Customers = {cust_count} 
    WHERE County = '{area}'"""
)
sql_update_customers_table_sme_sqlite3 = textwrap.dedent(
    """UPDATE SME_Customer_Count_Memory 
    SET Customer_Count = :customers, Last_Updated = ':date' 
    WHERE County_Name = ':area'"""
)
