"""

"""
import pyodbc


class DatabaseUtilities:

    def __init__(self, parser):
        self.connection = None
        self.connection_string = "DSN={database_name};UID={database_user};PWD={database_password}"
        self.cursor = None
        self.database_name = parser["DATABASE"]["NAME"]
        self.database_password = parser["DATABASE"]["PASSWORD"].format(money_sign="$")
        self.database_user = parser["DATABASE"]["USER"]
        self.delete_statement = "DELETE FROM RealTime_PowerOutages{style} WHERE PROVIDER = '{provider_abbrev}'"
        self.full_connection_string = None
        self.selection = None
        self.select_zipcode_by_provider_abbrev_statement_realtime = """SELECT zipcode FROM dbo.RealTime_PowerOutagesZipcodes WHERE PROVIDER = '{provider_abbrev}'"""
        self.select_by_provider_abbrev_statement_realtime = """SELECT {fields} FROM dbo.RealTime_PowerOutages{style} WHERE PROVIDER = '{provider_abbrev}'"""

    def create_database_connection_string(self):
        connection_string = self.connection_string.format(database_name=self.database_name,
                                                          database_user=self.database_user,
                                                          database_password=self.database_password)
        self.full_connection_string = connection_string
        return

    def create_database_cursor(self):
        self.cursor = self.connection.cursor()
        return

    def delete_cursor(self):
        del self.cursor
        self.cursor = None
        return

    def delete_records(self, style: str, provider_abbrev: str):
        # TODO: the provider syntax may not matter to sql. Assess need.
        table_name_style = {"ZIP": "Zipcodes", "County": "County"}.get(style)
        sql_statement = self.delete_statement.format(style=table_name_style,
                                                     provider_abbrev=provider_abbrev)
        print(sql_statement)
        self.cursor.execute(sql_statement)
        print(f"{provider_abbrev} {style} records deleted: {self.cursor.rowcount}")
        self.connection.commit()
        return

    def establish_database_connection(self):
        # NOTE: when the keyword 'p_str=' is used in pyodbc.connect(), a pyodbc.InterfaceError occurs
        with pyodbc.connect(self.full_connection_string) as connection:
            self.connection = connection
        return

    def fetch_all_from_selection(self):
        self.selection = None
        self.selection = self.cursor.fetchall()
        return

    # def select_records(self, style: str, provider_abbrev: str, fields_string: str = "*"):
    #     table_name_style = {"ZIP": "Zipcodes", "County": "County"}.get(style)
    #     sql_statement = self.select_by_provider_abbrev_statement_realtime.format(fields=fields_string,
    #                                                                              style=table_name_style,
    #                                                                              provider_abbrev=provider_abbrev)
    #     self.cursor.execute(sql_statement)
    #     return

    def execute_sql_statement(self, sql_statement):
        try:
            self.cursor.execute(sql_statement)
        except pyodbc.DataError:
            print(f"A value in the sql exceeds the field length allowed in database table: {sql_statement}")
        return

    # def insert_record_into_database(self, sql_statement):
    #     try:
    #         self.cursor.execute(sql_statement)
    #     except pyodbc.DataError:
    #         print(f"A value in the sql exceeds the field length allowed in database table: {sql_statement}")
    #     return

    def commit_changes(self):
        try:
            self.connection.commit()
        except Exception as e:
            print("Problem committing changes to database.")
            exit()
        return
