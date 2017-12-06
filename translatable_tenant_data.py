"""

"""
from weakref import WeakValueDictionary
from collections import defaultdict
from lxml import etree
from .__init__ import *

class Translatable_Tenant_Data(object):

    def __new__(cls, *args, **kwargs):
        if "key_list" not in cls.__dict__:
            cls.key_list = WeakValueDictionary()
        instance = object.__new__(cls)
        try:
            key = cls.generate_key(args[0], args[1], args[2])
            if key in cls.key_list:
                instance._duplicate = True
                instance._dup_item = cls.key_list[key]
            else:
                instance._duplicate = False
        except IndexError:
            pass
        return instance

    @classmethod
    def generate_key(cls, language, class_name, name):
        return "{}{}{}".format(language, class_name, name)

    def __init__(self, language, class_name, name, namespace, element=None):
        self._duplicate = False
        self._language = language
        self._class_name = class_name
        self._name = name
        self._namespace = namespace
        self._element = element
        self._has_translations = False
        self._translated_value_for_instance_data_dict = {}
        self._key = self.generate_key(language, class_name, name)
        self._WID_dict = defaultdict(list)
        self._error_strings = defaultdict(list)
        self._lock_translated_values = False
        self._seq = Seq_Generator().id
        return

    def change_lang(self, new_lang):
        self._language = new_lang
        self._element.find('{urn:com.workday/bsvc}User_Language_Reference')[0].text = new_lang
        self._key = Translatable_Tenant_Data.generate_key(self._language, self._class_name, self._name)
        return

    def add_parent(self, parent):
        self._parent = parent

    def get_csv_row(self):
        if API_VERSION in ['28.2',]:
            row = u"1,{},,{},{},{},{},".format("User_Language_ID", self._language, self._class_name, self._name,
                    self._namespace)
            if self.is_empty:
                yield u"{}\n".format(row)
            for td in self._translated_value_for_instance_data_dict.values():
                row += u"{}\n".format(td.get_csv_string())
                yield row
                row = u"1,,,,,,,"

    def put_translated_value_for_instance_data(self, trans_data):
        self._translated_value_for_instance_data_dict[trans_data.key] = trans_data
        trans_data.add_parent(self)
        if trans_data.has_translation:
            self._has_translations = True
        if trans_data.is_WID:
            self._WID_dict[trans_data.WID_key].append(trans_data)
        return

    def get_inconsistent_translations(self):
        pass
        """
            Check to see where we have identical base values translated differently
        """
        t_dict = {}
        for td in self._translated_value_for_instance_data_dict.values():
            if not td.has_translation:
                continue
            if td.base_value in t_dict:
                if t_dict[td.base_value].translated_value != td.translated_value:
                    self._error_strings[INCONSISTENT_TRANSLATION].append("[{}:{}:{}] has more than one translation".format(
                            self._parent.name, self._class_name, td))
            else:
                t_dict[td.base_value] = td
        return

    def remove_translated_value_for_instance_data(self, tvfid):
        print(u"My element is: {}".format(etree.tostring(self._element)))
        print(u"The element I'm removing is: {}".format(etree.tostring(tvfid.element)))
        self._element.remove(tvfid.element)
        del self._translated_value_for_instance_data_dict[tvfid.key]
        if tvfid.is_WID:
            del self._WID_dict[tvfid.key]
        return

    def remove_untranslated_data(self):
        del_list = []
        for key, d in self._translated_value_for_instance_data_dict.items():
            if not d.has_translation:
                self._element.remove(d.element)
                if d.is_WID:
                    del self._WID_dict[d.key]
                del_list.append(key)
        for k in del_list:
            del self._translated_value_for_instance_data_dict[k]
        return

    def get_translated_items(self):
        ret_list = []
        if self._has_translations:
            for td in self._translated_value_for_instance_data_dict.values():
                if td.has_translation:
                    ret_list.append(td)
        return ret_list

    def get_all_translatable_items(self):
        ret_list = []
        for td in self._translated_value_for_instance_data_dict.values():
            ret_list.append(td)
        return ret_list

    def update_translation(self, translation):
        """
            Passes a Trans_Data object, compare to my objects
            Should throw a KeyError if nothing found
        """
        if translation.is_WID:
            if not translation.WID_key in self._WID_dict:
                self._error_strings[NO_MATCHING_WID_KEY].append(u"[{}:{}:{}] has no matching WID key.".format(
                        self._parent.name, self._class_name, translation))
            for td in self._WID_dict[translation.WID_key]:
                td.add_translation(translation)
        else:
            self._translated_value_for_instance_data_dict[translation.key].add_translation(translation)
        return

    def get_error_strings(self):
        return self._error_strings

    def lock_translated_values(self):
        self._lock_translated_values = True
        for td in self._translated_value_for_instance_data_dict.values():
            if td.has_translation:
                td.lock()
        return
        

    @property
    def is_duplicate(self): return self._duplicate
    @property
    def key(self): return self._key
    @property
    def parent(self): return self._parent
    @property
    def language(self): return self._language
    @property
    def class_name(self): return self._class_name
    @property
    def name(self): return self._name
    @property
    def namespace(self): return self._namespace
    @property
    def element(self): return self._element
    @property
    def has_translations(self): return self._has_translations
    @has_translations.setter
    def has_translations(self, value):
        self._has_translations = value
        return
    @property
    def seq(self): return self._seq
    @property
    def has_errors(self):
        return len(self._error_strings) != 0
    @property
    def is_empty(self):
        return not len(self._translated_value_for_instance_data_dict)

    def __repr__(self):
        return "{}:{}:{}:{}:{}".format(self._seq, self._parent, self._language, self._class_name, self._name)
