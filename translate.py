#!/usr/bin/env python
"""
    As of Sep 2017 when this was first written it was designed to be used as follows:
    Craate a translation implentation suite. Add a task for each supported language
    OX that suite to the target tenant
    Now create populated templates for each language using WD xml. The file may 
    be zipped, but it should be just a single file per language.
    Do this for the source and destination tenant
    Now run this script, 
        translate.py <source file> <destination file>

        Source and destination file will remain unchanged, but a new file named out.xml will be created. 
        Load out.xml into the destination tenant.
        You can change the name using the -output_file_name option
    The files created by the tenants can be very large, if you want a smaller file to test with you can generate
    files by class name using the -class_name option. You can use it more than once
    TODO:
        Add database support
        Implement REST integration 
        Lots more comments
        Logging - validation, error, info
        Add timing count down

"""
from __init__ import *
from tenant import Tenant
from translatable_tenant_data import Translatable_Tenant_Data
from translated_value_for_instance_data import Translated_Value_for_Instance_Data
import sys
import argparse
import os.path
import codecs
from lxml import etree

def parse_command_line(cmd_args):
    parser = argparse.ArgumentParser(description=("Takes translation files from one tenant and"
            " puts the values into the file from another tenant"))

    sub = parser.add_subparsers()

    # This is the normal mode, take in xml files from two tenants and move the translations
    process_parser = sub.add_parser("process")
    process_parser.add_argument("source_file", metavar="<Source file>", help=("This is the source file"
            "- the file that has the translated values."))
    process_parser.add_argument("dest_file", metavar="<Destination file>", help=("This is the "
            "destination file - the file that receives the translated values."))
    process_parser.add_argument("-destination_name", help=("Name for the destination tenant."
            "Optional. If not provided the filename will be used."))
    process_parser.add_argument("-source_name", help=("Name for the source tenant. Optional."
            "If not provided the filename will be used."))
    process_parser.add_argument("-output_file_name", help=("Name for "
            "output file. If not provided it will be <destination file>-WITH_TRANSLATIONS.xml."))
    process_parser.add_argument("-class_name", action="append", default=[], help=("Generate files "
            "that contain only those class names. Generates files and quits."))
    process_parser.add_argument("-all_lines", default=False, action="store_true", help=("Default behavior "
            "is to remove all lines from destination file that do not contain translatable values, "
            "use this flag if you want all lines included in the destination file."))
    process_parser.add_argument("-v", "--validate_self", default=False, action="store_true", help=(
            "Perform validations against files. Current validations are to check for "
            "inconsistent translations and to check for source reference ids that do not "
            "exist in destination."))
    process_parser.add_argument("-respect", default=False, action="store_true", help=("Respects translated "
            "values in the destination tenant. Will not overwrite them"))
    process_parser.add_argument("-pretty", default=False, action="store_true", help=("Generates copies of "
            "source and destination xml files in human readable format (with spacing). *DO NOT* use "
            "these files as a source file for Workday as the spacing will break things. File will be "
            "the original file name with PRETTY as suffix before the .xml."))
    process_parser.add_argument("-examples", type=int, help=("Requires a number. Ouputs the first n examples "
            "that have changed in destination file so you can check after load into Workday."))
    process_parser.set_defaults(func=process)

    # Utility mode for combining multiple xml files into a single file
    combine_parser = sub.add_parser("combine")
    combine_parser.add_argument("Files to combine", nargs="+", help=("Provide a list of xml files to be combined into a "
            "single xml file. Generally used when combining generated files from different languages"))
    combine_parser.set_defaults(func=combine)

    # Utility mode for creating iLoad friendly csv files from xml files
    csv_parser = sub.add_parser("csv")
    csv_parser.add_argument("files_to_convert", metavar="Files to convert", nargs="+", help=("File(s) to convert to csv. "
            "File retains the same name with csv suffix. Input file is expected to "
            "be WD xml format. Output file is suitable for copy/paste directly into an iLoad file."))
    csv_parser.add_argument("-all_records", action="store_false", help=("By default the program will trim records "
            "without translations. Specify this flag all records are required."))
    csv_parser.set_defaults(func=csv)

    return parser.parse_args(cmd_args)


"""
    Convenience functions
"""
def p(e): return etree.tostring(e, pretty_print=True)
def pr(e): return etree.tostring(e, pretty_print=False)
def status(msg):
    global start_time
    global last_update_time

    now = int(time.time())
    time_elapsed = now - start_time
    time_since_last_update = now - last_update_time
    info(u"{} ({})".format(msg, time_elapsed))
    last_update_time = now
    return

def combine(flist, output_file_name):
    """
        Combines multiple xml files into one. It is designed to combine mulitple language files into a single
        file for loading.
    :param flist:
    :param output_file_name:
    :return:
    """
    filename = output_file_name
    #Translatable_Tenant_Data_Data
    # First we open the first file and use it as a base, then iterate through the rest

    base_tree = etree.parse(flist[0])
    base_root = base_tree.getroot()
    for f in flist[1:]:
        tree = etree.parse(f)
        root = tree.getroot()
        data = root.find('{urn:com.workday/bsvc}Translatable_Tenant_Data_Data')
        base_root.append(data)
    base_tree.write(filename)
    name = "{}.PRETTY{}".format(os.path.splitext(filename)[0],os.path.splitext(filename)[1])
    with open(name, "w") as f:
        f.write(p(base_root))
    return

def csv(args):
    """
    The args should be a list of one or more file names. The files should be WD xml formatted files
    Open the file, create a tenant object, and generate the csv
    :param args:
    :return:
    """
    for fname in args.files_to_convert:
        new_fname = "{}.{}".format(os.path.splitext(fname)[0], "csv")
        tenant = build_tenant(fname, new_fname)
        if not args.all_records:
            tenant.remove_untranslated_instances()
        status("Generating csv file named {}".format(new_fname))
        generate_csv_file(new_fname, tenant)
    return

def generate_csv_file(file_name, tenant):
    """
        Given a tenant, generate a csv file with named file_name
        csv file is designed to be copied directly into an iLoad file
    :param file_name:
    :param tenant:
    :return:
    """
    with codecs.open(file_name, "w", encoding="utf-8") as f:
        row_ctr = 0
        for row in tenant.get_csv_string():
            f.write(row)
            row_ctr += 1
            if not row_ctr % 25:
                break
                status("Class number {}".format(row_ctr))
            del(row)
    sys.exit()
    return

def build_tenant(file_name, tenant_name):
    """
        In this context tenant is the python object Tenant, not the WD tenant
        Almost all of the xml logic is here aside from adding a new 
        translated value
    """
    tree = etree.parse(file_name)
    root = tree.getroot()
    tenant = Tenant(tenant_name, tree, file_name)

    for trans_obj_xml in root.iterchildren():
        # You should be iterating through the Translatable_Tenant_Data_Data (name from iLoad)
        lang = trans_obj_xml.find('{urn:com.workday/bsvc}User_Language_Reference')[0].text
        class_name = trans_obj_xml.find('{urn:com.workday/bsvc}Class_Name').text
        try: # If we are not processing class_name was not an option
            if args.class_name and class_name not in args.class_name:
                root.remove(trans_obj_xml)
                continue
        except AttributeError:
            args.class_name = None #Avoid errors moving forward
        ar = trans_obj_xml.find('{urn:com.workday/bsvc}Attribute_Reference')
        name = ar.find('{urn:com.workday/bsvc}Name').text
        namespace = ar.find('{urn:com.workday/bsvc}Namespace_URI').text
        #print("lang {} class_name {} name {} namespace {}".format(lang, class_name, name, namespace))

        trans_obj = Translatable_Tenant_Data(lang, class_name, name, namespace, trans_obj_xml)

        for trans_data_xml in trans_obj_xml.findall('{urn:com.workday/bsvc}Translated_Value_for_Instance_Data'):
            ir = trans_data_xml.find('{urn:com.workday/bsvc}Instance_Reference')
            id_type = ir[0].attrib['{urn:com.workday/bsvc}type']
            try: # Either both exist or neither exists
                id_parent_type = ir[0].attrib['{urn:com.workday/bsvc}parent_type']
                id_parent_id = ir[0].attrib['{urn:com.workday/bsvc}parent_id']
            except KeyError:
                id_parent_type = ""
                id_parent_id = ""
            id_value = ir[0].text
            try:
                base_value = trans_data_xml.find('{urn:com.workday/bsvc}Base_Value').text
            except AttributeError:
                base_value = ""
            try:
                translated_value = trans_data_xml.find('{urn:com.workday/bsvc}Translated_Value').text
            except AttributeError:
                translated_value = ""
            try:
                rich_base_value = trans_data_xml.find('{urn:com.workday/bsvc}Rich_Base_Value').text
            except AttributeError:
                rich_base_value = ""
            try:
                translated_rich_value = trans_data_xml.find('{urn:com.workday/bsvc}Translated_Rich_Value').text
            except AttributeError:
                translated_rich_value = ""
            trans_data = Translated_Value_for_Instance_Data(id_type, id_value, id_parent_type, id_parent_id, base_value,
                    translated_value, rich_base_value, translated_rich_value, trans_data_xml)
            trans_obj.put_trans_data(trans_data)

        tenant.put_trans_obj(trans_obj)

    return tenant

def print_trans_data(tenant, trans_data):
    """
        Used to print out examples to the terminal that can be used for load validation
    """
    status(u"Example: {}".format(trans_data))
    args.examples -= 1
    if args.examples <= 0:
        tenant.unregister_updates()
    return

def process(args):

    # Confirm that files exist:
    if not (os.path.exists(args.source_file) and os.path.exists(args.dest_file)):
        print("Error - file does not exist\n{} = {}\n{} = {}".format(
                args.source_file, os.path.exists(args.source_file),
                args.dest_file, os.path.exists(args.dest_file)))
        sys.exit(1)

    # Set some defaults for file name / tenant name
    if not args.destination_name:
        args.destination_name = args.dest_file
    if not args.source_name:
        args.source_name = args.source_file

    # Ensure that the source and destination files are not the same
    if args.source_file == args.dest_file:
        print("Source file name and destination file name cannot be the same")
        sys.exit()

    # Ensure that files exist
    if not os.path.exists(args.source_file):
        error("Unable to find {}. Exitting.".format(args.source_file))
    if not os.path.exists(args.source_file):
        error("Unable to find {}. Exitting.".format(args.dest_file))
    if not (os.path.exists(args.source_file) and os.path.exists(args.dest_file)):
        sys.exit()

    status("Loading {}".format(args.source_name))
    source_tenant = build_tenant(args.source_file, args.source_name)
    print(source_tenant.get_stats())
    status("Loading {}".format(args.destination_name))
    dest_tenant = build_tenant(args.dest_file, args.destination_name)
    print(dest_tenant.get_stats())

    if args.pretty:
        for t in [source_tenant, dest_tenant]:
            name = "{}.PRETTY{}".format(os.path.splitext(t.file_name)[0],os.path.splitext(t.file_name)[1])
            status("Writing PRETTY version with filename: {}".format(name))
            with open(name, "w") as f:
                f.write(p(t.tree.getroot()))

    if args.respect:
        status("Respecting existing translated values in destination tenant")
        dest_tenant.lock_translated_values()

    # If this option as specified, the in-memory data will only have the class names
    # that were requested.
    if args.class_name:
        status("Filtering for class.")
        source_tenant.tree.write("{}.FILTERED.xml".format(args.source_name))
        dest_tenant.tree.write("{}.FILTERED.xml".format(args.destination_name))
        status("Created filtered files and exited")
        sys.exit()

    """ 
        We have loaded the files, now process them
        First, remove non-translated objects / data from the source
        Next, find matching items in destination and add translations
        Next, remove non-translated items in destination
        Finally, print out both files
    """
    # We do this for performance reasons, ignore lines that don't have values we care about
    status("Optimizing source file.")
    source_tenant.remove_untranslated_instances()


    # Perform validations as requested
    if args.validate_self:
        status("Validating")
        source_tenant.validate_self()
        print("{}".format(source_tenant.get_errors()))
        for t in source_tenant.get_translated_items():
            try:
                dest_tenant.add_translation(t)
            except KeyError:
                print(u"Failed to find matching entry for {}".format(t))

    status("Migrating translations")
    if args.examples:
        dest_tenant.register_updates(print_trans_data)
    for translated_item in source_tenant.get_translated_items():
        if translated_item.WID_key:
            debug(u"About to add translation:\n{}".format(translated_item))
            if translated_item.seq == 248044:
                debug(u"{}".format(p(translated_item.element)))
        try:
            dest_tenant.add_translation(translated_item)
        except KeyError:
            debug(u"Unable to find match for {}".format(translated_item))
            pass

    # Remove lines with no translated value unless requested to leave them in the file
    if not args.all_lines:
        status("Optimizing  output file")
        dest_tenant.remove_untranslated_instances()
    # Writing output file
    fname = args.output_file_name
    if not fname:
        fname = "{}-WITH_TRANSLATIONS.xml".format(os.path.splitext(args.dest_file)[0])

    with open(fname, "w") as f:
        status("Writing output file: {}".format(fname))
        f.write(etree.tostring(dest_tenant.tree.getroot()))
    if args.pretty:
        pretty_fname = "{}.PRETTY{}".format(os.path.splitext(fname)[0],os.path.splitext(fname)[1])
        with open(pretty_fname, "w") as f:
            status("Writing pretty output file: {}".format(pretty_fname))
            f.write(etree.tostring(dest_tenant.tree.getroot(), pretty_print=True))
    print(dest_tenant.get_stats())
    return

def main(cmd_args):
    global args, start_time, last_update_time

    debug("Called with arguments: {}".format(cmd_args))

    # Do some setup
    start_time = int(time.time())
    last_update_time = start_time

    args = parse_command_line(cmd_args)
    args.func(args)
    return

if __name__ == "__main__":
    main(sys.argv[1:])


