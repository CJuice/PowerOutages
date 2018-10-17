"""

"""
import pyodbc


class DatabaseUtilities:

    def __init__(self, parser):
        self.database_name = parser["DATABASE"]["NAME"]
        self.database_password = parser["DATABASE"]["PASSWORD"].format(money_sign="$")
        self.database_server = parser["DATABASE"]["SERVER"]
        self.database_user = parser["DATABASE"]["USER"]
        self.part_1_connection_string = "DRIVER={SQL Server};"
        self.part_2_connection_string = "Server={server};Database={name};UID={user};PWD={password};"
        self.full_connection_string = None

    def create_database_connection_string(self):
        part_2_completed = self.part_2_connection_string.format(server=self.database_server,
                                                                name=self.database_name,
                                                                user=self.database_user,
                                                                password=self.database_password)
        connection_string = f"{self.part_1_connection_string}{part_2_completed}"
        print("Database Connection String: ", connection_string)
        self.full_connection_string = connection_string

    def establish_database_connection(self):
        with pyodbc.connect(p_str=self.full_connection_string) as connection:
            return connection

