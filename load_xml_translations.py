#!/usr/bin/env python
"""
    As of Sep 2017 when this was first written it was designed to be used as follows:
    Craate a translation implentation suite. Add a task for each supported language
    OX that suite to the target tenant
    Now create populated templates for each language using WD xml. The file may 
    be zipped, but it should be just a single file per language.
    Do this for the source and destination tenant
    Now run this script, 
        load_xml_translations.py <source file> <destination file>

        Source and destination file will remain unchanged, but a new file named out.xml will be created. 
        Load out.xml into the destination tenant.
        You can change the name using the -output_file_name option
    The files created by the tenants can be very large, if you want a smaller file to test with you can generate
    files by class name using the -class_name option. You can use it more than once
    TODO:
        Add database support
        Implement REST integration 
        Lots more comments
        Validations
            Conflicting translations
            Non-WID objects / data with not existing in source but not dest

"""
from __init__ import *
from tenant import Tenant
from trans_obj import Trans_Obj
from trans_data import Trans_Data
import sys
import argparse
from lxml import etree

def parse_command_line():
    parser = argparse.ArgumentParser(description=("Takes translation files from one tenant and"
            " puts the values into the file from another tenant"))
    parser.add_argument("source_file", metavar="<Source file>", help=("This is the source file"
            "- the file that has the translated values"))
    parser.add_argument("dest_file", metavar="<Destination file>", help=("This is the "
            "destination file - the file that receives the translated values"))
    #parser.add_argument("-m", "--mode", default="XML", help="Defines the type of input (xml,db, etc)")
    parser.add_argument("-destination_name", help=("Name for the destination tenant."
            "Optional. If not provided the filename will be used."))
    parser.add_argument("-source_name", help=("Name for the source tenant. Optional."
            "If not provided the filename will be used."))
    parser.add_argument("-output_file_name", default="out.xml", help=("Name for "
            "output file. If not provided it will be out.xml"))
    parser.add_argument("-class_name", action="append", default=[], help=("Generate files "
            "that contain only those class names. Generates files and quits"))
    parser.add_argument("-all_lines", default=False, action="store_true", help=("Default behavior "
            "is to remove all lines from destination file that do not contain translatable values, "
            "use this flag if you want all lines included in the destination file."))
    parser.add_argument("-v", "--validate", default=False, action="store_true", help=(
            "Perform validations against files"))
    return parser.parse_args()

"""
    Convenience functions
"""
def p(e): return etree.tostring(e, pretty_print=True)
def pr(e): return etree.tostring(e, pretty_print=False)

def load_xml_data_into_tenant(file_name, tenant_name):
    """
        In this context texant is the object Tenant, not the WD tenant
        Almost all of the xml logic is here aside from adding a new 
        translated value
    """
    tree = etree.parse(file_name)
    root = tree.getroot()
    tenant = Tenant(tenant_name, tree)

    for trans_obj_xml in root.iterchildren():
        # You should be iterating through the Translatable_Tenant_Data_Data (name from iLoad)
        lang = trans_obj_xml.find('{urn:com.workday/bsvc}User_Language_Reference')[0].text
        class_name = trans_obj_xml.find('{urn:com.workday/bsvc}Class_Name').text
        if args.class_name and class_name not in args.class_name:
            root.remove(trans_obj_xml)
            continue
        ar = trans_obj_xml.find('{urn:com.workday/bsvc}Attribute_Reference')
        name = ar.find('{urn:com.workday/bsvc}Name').text
        namespace = ar.find('{urn:com.workday/bsvc}Namespace_URI').text
        #print("lang {} class_name {} name {} namespace {}".format(lang, class_name, name, namespace))

        trans_obj = Trans_Obj(lang, class_name, name, namespace, trans_obj_xml)

        for trans_data_xml in trans_obj_xml.findall('{urn:com.workday/bsvc}Translated_Value_for_Instance_Data'):
            ir = trans_data_xml.find('{urn:com.workday/bsvc}Instance_Reference')
            id_type = ir[0].attrib['{urn:com.workday/bsvc}type']
            id_value = ir[0].text
            try:
                base_value = trans_data_xml.find('{urn:com.workday/bsvc}Base_Value').text
            except AttributeError:
                base_value = None
            try:
                translated_value = trans_data_xml.find('{urn:com.workday/bsvc}Translated_Value').text
            except AttributeError as e:
                translated_value = None
            try:
                rich_base_value = trans_data_xml.find('{urn:com.workday/bsvc}Rich_Base_Value').text
            except AttributeError:
                rich_base_value = None
            try:
                translated_rich_value = trans_data_xml.find('{urn:com.workday/bsvc}Translated_Value').text
            except AttributeError as e:
                translated_rich_value = None
            #print(u"type {} val {} base {} trans {}".format(id_type, id_value, base_value, translated_value))
            trans_data = Trans_Data(id_type, id_value, base_value, translated_value, rich_base_value, 
                    translated_rich_value, trans_data_xml)
            trans_obj.put_trans_data(trans_data)

        tenant.put_trans_obj(trans_obj)

    return tenant


if __name__ == "__main__":
    
    args = parse_command_line()

    if not args.destination_name:
        args.destination_name = args.dest_file
    if not args.source_name:
        args.source_name = args.source_file

    if args.source_file == args.dest_file:
        print("Source file name and destination file name cannot be the same")
        sys.exit()

    source_tenant = load_xml_data_into_tenant(args.source_file, args.source_name)
    dest_tenant = load_xml_data_into_tenant(args.dest_file, args.destination_name)

    # If this option as specified, the in-memory data will only have the class names
    # that were requested.
    if args.class_name:
        source_tenant.tree.write("{}.FILTERED.xml".format(args.source_name))
        dest_tenant.tree.write("{}.FILTERED.xml".format(args.destination_name))
        print("Created filtered files and exited")
        sys.exit()

    """ 
        We have loaded the files, now process them
        First, remove non-translated objects / data from the source
        Next, find matching items in destination and add translations
        Next, remove non-translated items in destination
        Finally, print out both files
    """
    source_tenant.remove_empty_translations()

    for translated_item in source_tenant.get_translated_items():
        dest_tenant.add_translation(translated_item)

    # Perform validations is requested
    if args.validate:
        source_tenant.validate()

    # Remove lines with no translated value unless requested to leave them in the file
    if not args.all_lines:
        dest_tenant.remove_empty_translations()
    dest_tenant.tree.write(args.output_file_name)
