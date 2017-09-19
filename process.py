#!/usr/bin/env python
import sys

PATH_TO_DIR = "/Users/<user>/py"
FILE_LIST = "files_to_process"

# Supported actions "translate" "csv" "combine", you must uncomment one
ACTION = "translate"
#ACTION = "csv"
#ACTION = "combine"

# NOTE: On options, if you do not want an option then put a '#' at the beginning of the line

sys.path.append(PATH_TO_DIR)

from wd_translations import translate as engine

if ACTION == "translate":
    with open(FILE_LIST, "r") as f:
        for l in f:
            l = l.split()

            # OPTIONS BELOW
            # -pretty will generate a "nice" xml version of the target file in addition to the file to load
            # DO NOT USE the file with the word "PRETTY" in it to load to WD, it will fail
            l.append("-pretty")
            l.append("-respect") # Will not overwrite existing translations in destination tenant

            l.insert(0, "process")
            print("Calling with arguments: {}".format(l))
            engine.main(l)

elif ACTION == "csv":
    with open(FILE_LIST, "r") as f:
        for l in f:
            l = l.split()
            #l.append("-all-records") # Not recommended. Will include all records, including those w/ no translation
            l.insert(0, "csv")
            print("Calling with arguments: {}".format(l))
            engine.main(l)

elif ACTION == "combine":
    with open(FILE_LIST, "r") as f:
        flist = []
        for l in f:
            flist.append(l)
        flist.insert(0, "csv")
        print("Calling with arguments: {}".format(flist))
        engine.main(flist)


