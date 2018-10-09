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

    def establish_database_connection(self):
        part_2_completed = self.part_2_connection_string.format(server=self.database_server,
                                                                name=self.database_name,
                                                                user=self.database_user,
                                                                password=self.database_password)
        connection_string = f"{self.part_1_connection_string}{part_2_completed}"
        print(connection_string)
        with pyodbc.connect(p_str=connection_string) as connection:
            return connection

