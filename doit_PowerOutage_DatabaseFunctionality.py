"""
Module containing DatabaseUtilities class for functionality related to database interaction.
"""

import pyodbc
import PowerOutages.doit_PowerOutage_CentralizedVariables as VARS


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

    def commit_changes(self) -> None:
        """
        Commit changes to database.
        :return: None
        """
        try:
            self.connection.commit()
        except Exception as e:
            print("Problem committing changes to database.")
            exit()
        return None

    def create_database_connection_string(self) -> None:
        """
        Create the connection string for accessing database and assign to internal attribute.
        :return: None
        """
        self.full_connection_string = self.database_connection_string.format(database_name=self.database_name,
                                                                             database_user=self.database_user,
                                                                             database_password=self.database_password)
        return None

    def create_database_cursor(self) -> None:
        """
        Create a database cursor for use.
        :return: None
        """
        self.cursor = self.connection.cursor()
        return None

    def delete_cursor(self) -> None:
        """
        Delete existing database cursor.
        :return: None
        """
        del self.cursor
        self.cursor = None
        return None

    def delete_records(self, style: str, provider_abbrev: str) -> None:
        """
        Substitute values into delete sql statement, execute, and commit.

        :param style: ZIP or County
        :param provider_abbrev: abbreviation of the provider
        :return: None
        """
        table_name_style = {"ZIP": "Zipcodes", "County": "County"}.get(style)
        sql_statement = self.sql_delete_statement.format(style=table_name_style,
                                                         provider_abbrev=provider_abbrev)
        self.cursor.execute(sql_statement)
        print(f"{provider_abbrev} {style} records deleted: {self.cursor.rowcount}")
        self.connection.commit()
        return None

    def establish_database_connection(self) -> None:
        """
        Establish a connection.
        NOTE: when the keyword 'p_str=' is used in pyodbc.connect(), a pyodbc.InterfaceError occurs
        :return: None
        """

        with pyodbc.connect(self.full_connection_string) as connection:
            self.connection = connection
        return None

    def execute_sql_statement(self, sql_statement) -> None:
        """
        Execute the passed sql statement
        :param sql_statement: sql statement to execute
        :return: None
        """
        try:
            self.cursor.execute(sql_statement)
        except pyodbc.DataError:
            print(f"A value in the sql exceeds the field length allowed in database table: {sql_statement}")
        return None

    def fetch_all_from_selection(self) -> None:
        """
        Fetch all records from a selection from a database.
        :return: None
        """
        self.selection = None
        self.selection = self.cursor.fetchall()
        return None

