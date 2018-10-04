# ______________________________________________
"""
Generic setup
"""
import configparser
import os
# import PowerOutages_V2.doit_PowerOutage_BGEClasses as BGEMod
import PowerOutages_V2.doit_PowerOutage_CTKClasses as CTKMod
# import PowerOutages_V2.doit_PowerOutage_DatabaseFunctionality as DbMod
# import PowerOutages_V2.doit_PowerOutage_DELClasses as DELMod
# import PowerOutages_V2.doit_PowerOutage_EUCClasses as EUCMod
# import PowerOutages_V2.doit_PowerOutage_FESClasses as FESMod
# import PowerOutages_V2.doit_PowerOutage_PEPClasses as PEPMod
import PowerOutages_V2.doit_PowerOutage_ProviderClasses as ProvMod
# import PowerOutages_V2.doit_PowerOutage_SMEClasses as SMEMod


_root_project_path = os.path.dirname(__file__)
credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
parser.read(filenames=["doit_PowerOutage_Credentials.cfg", "doit_PowerOutage_CentralizedVariables.cfg"])



# ______________________________________________
# Storing for later use, if needed.
# style_to_class_type_dict = {"XML": ProvMod.ProviderXML,
#                                 "JSON": ProvMod.ProviderJSON,
#                                 "BGE": ProvMod.ProviderBGE,
#                                 }
# provider_inventory_dict = {"BGE": ProvMod.ProviderDetails(False, "BGE"),
#                            "CTK": ProvMod.ProviderDetails(True, "XML"),
#                            "DEL": ProvMod.ProviderDetails(False, "JSON"),
#                            "EUC": ProvMod.ProviderDetails(False, "XML"),
#                            "FES": ProvMod.ProviderDetails(False, "XML"),
#                            "PEP": ProvMod.ProviderDetails(False, "JSON"),
#                            "SME": ProvMod.ProviderDetails(True, "JSON"),
#                            }
#
# # Need to instantiate all providers objects according to their type and store by abbreviation key
# objects_dict = {}
# for key, value in provider_inventory_dict.items():
#     class_type_object = style_to_class_type_dict[value.style]
#     objects_dict[key] = class_type_object(config_parser=parser, provider_abbrev=key, style=value.style, dual_feed=value.dual_feed)
# print(objects_dict)
#
# # Need to get and assign attributes
# county_root = "County_"
# zip_root = "ZIP_"
# for key, obj in objects_dict.items():
#     # print(obj.style)
#     print(obj.abbrev, obj.dual_feed)
#     county_config_section_name = f"{county_root}{key}"
#     zip_config_section_name = f"{zip_root}{key}"
#     if obj.dual_feed:
#         obj.metadata_feed_uri = parser[county_config_section_name]["metadata_uri"]
#         obj.data_feed_uri = parser[county_config_section_name]["data_feed_uri"]
#         obj.date_created_uri = parser[county_config_section_name]["date_created_uri"]
#     else:
#         pass
#
#     print(obj.metadata_feed_uri, obj.data_feed_uri, obj.date_created_uri)
#
# exit()
# ______________________________________________
exit()
"""
Instantiate xml provider, use config to get uri, make web request for xml data feed content, parse xml and 
extract value.
"""

# Instantiate provider object
ctk_obj = CTKMod.CTK(provider_abbrev="CTK")

# Get the data feed uri from config file
ctk_obj.data_feed_uri = ProvMod.Provider.get_config_variable(parser=parser,
                                                             section="County_CTK",
                                                             variable_name="data_feed_uri")

# Make a web request and assign response to object attribute
ctk_obj.data_feed_response = ctk_obj.web_func_class.make_web_request(uri=ctk_obj.data_feed_uri)

# Parse the xml into a dom object. Pull a tag element and an attribute string.
ctk_obj.xml_dom = ctk_obj.prov_xml_class.process_xml_response_to_DOM(
    response_xml_str=ctk_obj.data_feed_response.text)
tag_element_date_generated = ctk_obj.prov_xml_class.extract_xml_tag_element(xml_dom=ctk_obj.xml_dom,
                                                                            tag_name="generated",
                                                                            tag_index=0)
generated_date_str = ctk_obj.prov_xml_class.extract_attribute_from_xml_tag_element(
    xml_element=tag_element_date_generated,
    attribute_name="date")

print(generated_date_str)

# ______________________________________________
exit()
"""
Exploring use of ENUM in Python. Recalled these from Java.
Didn't know they were in Python.
"""
from enum import Enum, auto, unique


@unique
class ProviderAbbrevs(Enum):
    BEG = auto()
    CTK = auto()
    DEL = auto()
    EUC = auto()
    FES = auto()
    PEP = auto()
    SME = auto()


l = list(ProviderAbbrevs)
print(l)
p = ProviderAbbrevs.BEG
print(p.name)
print(p.value)
# ______________________________________________
