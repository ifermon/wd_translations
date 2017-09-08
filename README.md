usage: load_xml_translations.py [-h] [-destination_name DESTINATION_NAME]
                                [-source_name SOURCE_NAME]
                                [-output_file_name OUTPUT_FILE_NAME]
                                [-class_name CLASS_NAME] [-all_lines] [-v]
                                [-respect] [-pretty] [-examples EXAMPLES]
                                <Source file> <Destination file>

Takes translation files from one tenant and puts the values into the file from
another tenant

positional arguments:
  <Source file>         This is the source file- the file that has the
                        translated values
  <Destination file>    This is the destination file - the file that receives
                        the translated values

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
                        <destination file>-WITH_TRANSLATIONS.xml
  -class_name CLASS_NAME
                        Generate files that contain only those class names.
                        Generates files and quits
  -all_lines            Default behavior is to remove all lines from
                        destination file that do not contain translatable
                        values, use this flag if you want all lines included
                        in the destination file.
  -v, --validate        Perform validations against files
  -respect              Respects translated values in the destination tenant.
                        Will not overwrite them
  -pretty               Generates copies of source and destination xml files
                        in human readable format (with spacing). *DO NOT* use
                        these files as a source file for program. The spaces
                        will break things. File will be the original file name
                        with PRETTY as suffix before the .xml
  -examples EXAMPLES    Requires a number. Ouputs the first n examples that
                        have changed in destination file so you can check
                        after load
