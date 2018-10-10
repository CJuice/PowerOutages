"""

"""

class PEPDELParent():
    COUNTY_DB_UPDATE_STATEMENT = """exec RealTime_UpdatePowerOutagesCounty {outage}, '{county}', '{provider}', '{state}'"""
    ZIP_DB_UPDATE_STATEMENT = """"exec RealTime_UpdatePowerOutagesZip {outage}, '{zip_code}', '{provider}'"""

    def __init__(self):
        super(PEPDELParent, self).__init__()