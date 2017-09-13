"""

"""

from enum import Enum

class Source_Type(Enum):
    XML = 1

class Error_Type(Enum):
    INCONSISTENT_TRANSLATION = "Within a single object there are two identical strings are translated differently."
    NO_MATCHING_WID_KEY = "There is no matching WID."
    NO_MATCHING_REF_ID = "There is no matching reference ID in the target tenant."
    NO_MATCHING_CLASS_NAME = "There is no matching class name in the target tenant."
