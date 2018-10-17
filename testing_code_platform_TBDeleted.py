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
import xml.etree.ElementTree as ET
from PowerOutages_V2.doit_PowerOutage_UtilityClass import Utility as doit_util
import xml.etree.ElementTree as ET

_root_project_path = os.path.dirname(__file__)
credentials_path = os.path.join(_root_project_path, "doit_PowerOutage_Credentials.cfg")
centralized_variables_path = os.path.join(_root_project_path, "doit_PowerOutage_CentralizedVariables.cfg")
parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
parser.read(filenames=["doit_PowerOutage_Credentials.cfg", "doit_PowerOutage_CentralizedVariables.cfg"])


def myfun(element):
    ls = []
    for child in element:
        ls.append(child)
    return ls

# body, dataresponse, dataresult = None, None, None

with open("BGE_XML_ZIPsample.xml", "r") as handler:
    contents = handler.read()
    root = ET.fromstring(contents)
    for dt in root.iter("CreateDateTime"):
        print(dt.text)
    exit()

    outage_elements_list = []
    for outage in root.iter("Outage"):
        outage_elements_list.append(outage)
    for outage in outage_elements_list:
        area, cust = outage.find("ZipCode"), outage.find("CustomersOut")
        area_text, cust_text = area.text, cust.text
        print(area_text, cust_text)
    exit()


    outage_elements_list = []
    for outage in root.iter("Outage"):
        outage_elements_list.append(outage)
    outage_details_list = []
    for o in outage_elements_list:
        area, cust = [child for child in o]
        print(area, cust)
        outage_details_list.append((area, cust))
    for tup in outage_details_list:
        area_text, affected_text = tup[0].text, tup[1].text
        print(area_text, affected_text)
    exit()


    body = [child for child in root][0]
    dataresponse = [child for child in body][0]
    dataresult = [child for child in dataresponse][0]
    responseheader, outages = [child for child in dataresult]
    print(responseheader, outages)
    print([child for child in responseheader])
    print([child for child in outages])
    # print([(child.tag, doit_util.extract_feature_from_element(element=child, tag_name="CreateDateTime")) for child in responseheader])
    print(type(doit_util.extract_all_immediate_child_features_from_element(element=responseheader, tag_name="CreateDateTime")))
    m = doit_util.extract_first_immediate_child_feature_from_element(element=responseheader, tag_name="CreateDateTime")
    print(m)
    print(m.text)
    # l = doit_util.extract_all_features_from_element(element=responseheader, tag_name="CreateDateTime")
    # print(len(l))
    # print(l[0])
    # for child in root:
    #     print(child.tag, child.attrib)
    #     body = child
    # for child in body:
    #     print(child.tag, child.attrib)
    #     dataresponse = child
    # for child in dataresponse:
    #     print(child.tag, child.attrib)
    #     dataresult = child
    # rh, outs = [child for child in dataresult]
    # print(rh, outs)
    # out_ls = [child for child in outs]
    # print(out_ls)

exit()
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
ctk_obj.xml_dom = ctk_obj.prov_xml_class.convert_xml_response_to_DOM(
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
