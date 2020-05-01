"""
Module containing DatabaseUtilities class for functionality related to database interaction.

"""
import pyodbc
import PowerOutages_V2.doit_PowerOutage_CentralizedVariables as VARS


class DatabaseUtilities:
    """
    For functionality related to database interaction.
    """
    def __init__(self, parser):
        self.connection = None
        self.database_connection_string = VARS.database_connection_string
        self.cursor = None
        self.database_name = parser["DATABASE"]["NAME"]
        self.database_password = parser["DATABASE"]["PASSWORD"].format(money_sign="$")
        self.database_user = parser["DATABASE"]["USER"]
        self.sql_delete_statement = VARS.sql_delete_statement
        self.full_connection_string = None
        self.selection = None
        self.sql_select_zipcode_by_provider_abbrev_statement_realtime = VARS.sql_select_zip_by_provider_abbrev_realtime
        self.sql_select_by_provider_abbrev_statement_realtime = VARS.sql_select_by_provider_abbrev_realtime

    def commit_changes(self):
        """
        Commit changes to database.
        :return:
        """
        try:
            self.connection.commit()
        except Exception as e:
            print("Problem committing changes to database.")
            exit()
        return

    def create_database_connection_string(self):
        """
        Create the connection string for accessing database and assign to internal attribute.
        :return: none
        """
        self.full_connection_string = self.database_connection_string.format(database_name=self.database_name,
                                                                             database_user=self.database_user,
                                                                             database_password=self.database_password)
        return

    def create_database_cursor(self):
        """
        Create a database cursor for use.
        :return: none
        """
        self.cursor = self.connection.cursor()
        return

    def delete_cursor(self):
        """
        Delete existing database cursor.
        :return: none
        """
        del self.cursor
        self.cursor = None
        return

    def delete_records(self, style: str, provider_abbrev: str):
        """
        Substitute values into delete sql statement, execute, and commit.

        :param style: ZIP or County
        :param provider_abbrev: abbreviation of the provider
        :return: none
        """
        table_name_style = {"ZIP": "Zipcodes", "County": "County"}.get(style)
        sql_statement = self.sql_delete_statement.format(style=table_name_style,
                                                         provider_abbrev=provider_abbrev)
        self.cursor.execute(sql_statement)
        print(f"{provider_abbrev} {style} records deleted: {self.cursor.rowcount}")
        self.connection.commit()
        return

    def establish_database_connection(self):
        """
        Establish a connection.
        NOTE: when the keyword 'p_str=' is used in pyodbc.connect(), a pyodbc.InterfaceError occurs
        :return:
        """
        #
        with pyodbc.connect(self.full_connection_string) as connection:
            self.connection = connection
        return

    def execute_sql_statement(self, sql_statement):
        """
        Execute the passed sql statement
        :param sql_statement: sql statement to execute
        :return: none
        """
        try:
            self.cursor.execute(sql_statement)
        except pyodbc.DataError:
            print(f"A value in the sql exceeds the field length allowed in database table: {sql_statement}")
        return

    def fetch_all_from_selection(self):
        """
        Fetch all records from a selection from a database.
        :return: none
        """
        self.selection = None
        self.selection = self.cursor.fetchall()
        return

