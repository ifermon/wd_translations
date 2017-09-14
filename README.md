Description:
    This is a script that will help with the *migration* of translations from tenant to tenant. Specifically you are going to want to use it when you are building a new tenant because of issues you will face with WIDs and changing / DNU reference IDs. If you are moving from one COPY of a tenant to another copy then the WIDs will match and you should just use the Workday XML files. 

Note on Workday XML files. Tranlsations are huge. Workday makes you create a new implementation task for each language. If you generate a populated iLoad template it will be a zip file that will contain many (3+) iLoad files. Instead always use the Workday XML file as that will allow you to only have one file per language. 


Instructions:

This has been tested on Mac only. 

To install: 
    Download the script from https://github.com/ifermon/wd_translations as a zip file.
    Unzip the file. It will expand into a directory. It's not installed.

To use:

See usage instructions below. It requires using the command line from the teminal. 

Just before using you are going to want to generate populated Workday XML templates for all of your languages in both of your tenants (the source ttenant and the destination tenant).

Important - you can only do this *after* you have completed the configuration on your destination tenant.



usage: load_xml_translations.py [-h] {process,combine,csv} ...

Takes translation files from one tenant and puts the values into the file from
another tenant

positional arguments:
  {process,combine,csv}

optional arguments:
  -h, --help            show this help message and exit

usage: load_xml_translations.py process [-h]
                                        [-destination_name DESTINATION_NAME]
                                        [-source_name SOURCE_NAME]
                                        [-output_file_name OUTPUT_FILE_NAME]
                                        [-class_name CLASS_NAME] [-all_lines]
                                        [-v] [-respect] [-pretty]
                                        [-examples EXAMPLES]
                                        <Source file> <Destination file>

positional arguments:
  <Source file>         This is the source file- the file that has the
                        translated values.
  <Destination file>    This is the destination file - the file that receives
                        the translated values.

optional arguments:
  -h, --help            show this help message and exit
  -destination_name DESTINATION_NAME
                        Name for the destination tenant.Optional. If not
                        provided the filename will be used.
  -source_name SOURCE_NAME
                        Name for the source tenant. Optional.If not provided
                        the filename will be used.
  -output_file_name OUTPUT_FILE_NAME
                        Name for output file. If not provided it will be
                        <destination file>-WITH_TRANSLATIONS.xml.
  -class_name CLASS_NAME
                        Generate files that contain only those class names.
                        Generates files and quits.
  -all_lines            Default behavior is to remove all lines from
                        destination file that do not contain translatable
                        values, use this flag if you want all lines included
                        in the destination file.
  -v, --validate_self   Perform validations against files. Current validations
                        are to check for inconsistent translations and to
                        check for source reference ids that do not exist in
                        destination.
  -respect              Respects translated values in the destination tenant.
                        Will not overwrite them
  -pretty               Generates copies of source and destination xml files
                        in human readable format (with spacing). *DO NOT* use
                        these files as a source file for Workday as the
                        spacing will break things. File will be the original
                        file name with PRETTY as suffix before the .xml.
  -examples EXAMPLES    Requires a number. Ouputs the first n examples that
                        have changed in destination file so you can check
                        after load into Workday.

usage: load_xml_translations.py combine [-h]
                                        Files to combine
                                        [Files to combine ...]

positional arguments:
  Files to combine  Provide a list of xml files to be combined into a single
                    xml file. Generally used when combining generated files
                    from different languages

optional arguments:
  -h, --help        show this help message and exit
usage: load_xml_translations.py csv [-h]
                                    Files to convert [Files to convert ...]

positional arguments:
  Files to convert  File(s) to convert to csv. File retains the same name with
                    csv suffix. Input file is expected to be WD xml format.
                    Output file is suitable for copy/paste directly into an
                    iLoad file.

optional arguments:
  -h, --help        show this help message and exit
