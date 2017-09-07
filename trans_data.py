"""

"""


class Trans_Data(object):

    def __init__(self, id_type, id_value, base_value, translated_value, element=None):
        self._id_type = id_type
        self._id_value = id_value
        self._base_value = base_value
        self._translated_value = translated_value
        if translated_value:
            self._has_translation = True
        else:
            self._has_translation = False
        self._element = element
        self._key = u"{}{}{}".format(id_type, id_value, base_value)
        if self._id_type == "WID":
            self._is_WID = True
            self._WID_key = "{}{}".format(id_type, base_value)
        else:
            self._is_WID = False
            self._WID_key = None
        return

    def add_parent(self, parent):
        self._parent = parent
        return

    def add_translation(self, translation):
        """
            translation is a Trans_Data object
        """
        self._translated_value = translation.translated_value
        e = translation.element.find('{urn:com.workday/bsvc}Translated_Value')
        self._element.append(e)
        self._has_translation = True
        return

    @property
    def WID_key(self):
        return self._WID_key
    @property
    def is_WID(self):
        return self._is_WID
    @property
    def key(self):
        return self._key
    @property
    def parent_key(self):
        return self._parent.key
    @property
    def parent(self):
        return self._parent
    @property
    def id_type(self):
        return self._id_type
    @property
    def id_value(self):
        return self._id_value
    @property
    def base_value(self):
        return self._base_value
    @property
    def translated_value(self):
        return self._translated_value
    @property
    def element(self):
        return self._element
    @property
    def has_translation(self):
        return self._has_translation
