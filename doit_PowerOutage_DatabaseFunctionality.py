"""

"""
import pyodbc


class DatabaseUtilities:

    def __init__(self, parser):
        self.connection_string = "DSN={database_name};UID={database_user};PWD={database_password}"
        self.database_name = parser["DATABASE"]["NAME"]
        self.database_password = parser["DATABASE"]["PASSWORD"].format(money_sign="$")
        self.database_user = parser["DATABASE"]["USER"]
        # self.database_server = parser["DATABASE"]["SERVER"]
        self.full_connection_string = None

    def create_database_connection_string(self):
        connection_string = self.connection_string.format(database_name=self.database_name,
                                                          database_user=self.database_user,
                                                          database_password=self.database_password)
        print("Database Connection String: ", connection_string)
        self.full_connection_string = connection_string

    def establish_database_connection(self):
        # NOTE: when the keyword 'p_str=' is used in pyodbc.connect(), a pyodbc.InterfaceError occurs
        with pyodbc.connect(self.full_connection_string) as connection:
            return connection
