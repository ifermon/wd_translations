try:
    from .my_type import Source_Type
    from .my_type import Error_Type
except SystemError:
    from my_type import Source_Type
    from my_type import Error_Type


XML = Source_Type.XML
INCONSISTENT_TRANSLATION = Error_Type.INCONSISTENT_TRANSLATION
NO_MATCHING_WID_KEY = Error_Type.NO_MATCHING_WID_KEY
API_VERSION = '28.2'


"""
    Set up logging here
    We are going to have two loggers, one for debugging/errors, 
    one for logging validation errors
"""
import logging as l
import time
import sys

from distutils.version import LooseVersion
if sys.version_info < (3, 4):
    raise "Must use python version 3.4 or greater. (Hint: did you use python3?)"

main_logger = l.getLogger("wd_translations")
debug = main_logger.debug
info = main_logger.info
error = main_logger.error

validation_logger = l.getLogger("validation")
validation = validation_logger.info

if not len(main_logger.handlers):
    # Setup logging (declared in __init__.py)
    timestamp = time.strftime("%m%d%Y-%H.%M.%S%z")
    main_logger.setLevel(l.DEBUG)
    sh = l.StreamHandler()
    sh.setLevel(l.INFO)
    sh.setLevel(l.DEBUG)
    fh = l.FileHandler("Translations_Log_File-{}.txt".format(timestamp))
    fhformatter = l.Formatter(datefmt="%y%m%d-%H%M%S%z",
                              fmt="%(asctime)-22s %(message)s [%(filename)s@%(lineno)s]FH")
    fh.setFormatter(fhformatter)
    fh.setLevel(l.DEBUG)
    main_logger.addHandler(fh)
    main_logger.addHandler(sh)
    val_fh = l.FileHandler("Validations-{}.txt".format(timestamp))
    validation_logger.addHandler(val_fh)
    validation_logger.setLevel(l.INFO)

import itertools
class Seq_Generator():
    newid = itertools.count().__next__
    def __init__(self):
        self.id = Seq_Generator.newid()
