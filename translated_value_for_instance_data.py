"""

"""

import sys
from lxml import etree
from copy import deepcopy
def p(e): return etree.tostring(e, pretty_print=True)

seq = 0

class Translated_Value_for_Instance_Data(object):

    def __init__(self, id_type, id_value, base_value=None, translated_value=None, rich_base_value=None, translated_rich_value=None, element=None):
        global seq
        self._id_type = id_type
        self._id_value = id_value
        self._base_value = base_value
        self._translated_value = translated_value
        self._rich_base_value = rich_base_value
        self._translated_rich_value = translated_rich_value
        self._locked = False
        self._parent = None
        self._seq = seq
        seq += 1
        if translated_value or translated_rich_value:
            self._has_translation = True
        else:
            self._has_translation = False
        self._element = element
        self._key = u"{}{}{}".format(id_type, id_value, base_value)
        if self._id_type == "WID":
            self._is_WID = True
            self._WID_key = u"{}{}".format(id_type, base_value)
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
            If I have an existing value, remove it first before adding the new one
        """
        if not self._locked:
            self.remove_translation()
            self._translated_value = translation.translated_value
            e = translation.element.find('{urn:com.workday/bsvc}Translated_Value')
            if e is not None:
                self._element.append(deepcopy(e))
            e = translation.element.find('{urn:com.workday/bsvc}Translated_Rich_Value')
            if e is not None:
                self._element.append(deepcopy(e))
            self._has_translation = True

            self.parent.has_translations = True
        return

    def remove_translation(self):
        """
            Removes an existing translation if exists but keeps object in place
        :return:
        """
        try:
            if self._has_translation:
                if self._translated_value:
                    find_str = '{urn:com.workday/bsvc}Translated_Value'
                else:
                    find_str = '{urn:com.workday/bsvc}Translated_Rich_Value'
                e = self._element.find(find_str)
                print("self._seq {}".format(self._seq))
                print("Removing {}".format(p(e)))
                self._element.remove(e)
        except:
            print("Error removing my translated value")
            print("_has_translation: {}".format(self._has_translation))
            print(u"Trans value = {}".format(self._translated_value))
            print(u"Here I am {}".format(self))
            print(u"And my element tree: {}".format(p(self.element)))
            sys.exit()
        return

    def lock(self):
        self._locked = True
        return


    @property
    def WID_key(self): return self._WID_key
    @property
    def is_WID(self): return self._is_WID
    @property
    def key(self): return self._key
    @property
    def parent_key(self): return self._parent.key
    @property
    def parent(self): return self._parent
    @property
    def id_type(self): return self._id_type
    @property
    def id_value(self): return self._id_value
    @property
    def base_value(self): return self._base_value
    @property
    def translated_value(self): return self._translated_value
    @property
    def rich_base_value(self): return self._rich_base_value
    @property
    def translated_rich_value(self): return self._translated_rich_value
    @property
    def element(self): return self._element
    @property
    def has_translation(self): return self._has_translation
    @property
    def is_locked(self): return self._locked
    @property
    def seq(self): return self._seq


    def __repr__(self):
        return u"{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}".format(self._seq, self.parent, self.id_type, self.id_value,
                self.base_value, self.translated_value, self.rich_base_value, self.translated_rich_value,
                self.has_translation, self.is_WID, self._WID_key)
