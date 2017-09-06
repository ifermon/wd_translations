"""

"""


class Trans_Data(object):

    def __init__(self, id_type, id_value, base_value, translated_value, element=None):
        self._id_type = id_type
        self._id_value = id_value
        self._base_value = base_value
        self._translated_value = translated_value
        if translated_value is None:
            self._has_translation = False
        else:
            self._has_translation = True
        self._element = element
        if id_type == "WID":
            self._key = "{}{}".format(id_type, base_value)
        else:
            self._key = "{}{}{}".format(id_type, id_value, base_value)
        return

    def add_parent(self, parent):
        self._parent = parent
        return

    def add_translation(self, t_str):
        self._translated_value = t_str
        e = t_str.element.find('{urn:com.workday/bsvc}Translated_Value')
        self._element.append(e)
        self._has_translation = True
        return

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
