from collections import defaultdict
"""

"""

class Trans_Obj(object):

    def __init__(self, language, class_name, name, namespace, element=None):
        self._language = language
        self._class_name = class_name
        self._name = name
        self._namespace = namespace
        self._element = element
        self._has_translations = False
        self._trans_data_dict = {}
        self._key = "{}{}{}{}".format(language, class_name, name, namespace)
        self._WID_dict = defaultdict(list)
        self._error_strings = defaultdict(list)
        self._lock_translated_values = False
        return

    def add_parent(self, parent):
        self._parent = parent

    def put_trans_data(self, trans_data):
        self._trans_data_dict[trans_data.key] = trans_data
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
        for td in self._trans_data_dict.values():
            if not td.has_translation:
                continue
            if td.base_value in t_dict:
                if t_dict[td.base_value].translated_value != td.translated_value:
                    self._error_strings[INCONSISTENT_TRANSLATION].append("[{}:{}:{}] has more than one translation".format(
                            self._parent.name, self._class_name, td))
            else:
                t_dict[td.base_value] = td
        return

    def remove_untranslated_data(self):
        for key, d in self._trans_data_dict.items():
            if not d.has_translation:
                self._element.remove(d.element)
                del self._trans_data_dict[key]
        return

    def get_translated_items(self):
        ret_list = []
        if self._has_translations:
            for td in self._trans_data_dict.values():
                if td.has_translation:
                    ret_list.append(td)
        return ret_list

    def update_translation(self, translation):
        """
            Passes a Trans_Data object, compare to my objects
        """
        if translation.is_WID:
            for td in self._WID_dict[translation.WID_key]:
                td.add_translation(translation)
        else:
            self._trans_data_dict[translation.key].add_translation(translation)
        return

    def get_error_strings(self):
        return self._error_strings

    def lock_translated_values(self):
        self._lock_translated_values = True
        for td in self._trans_data_dict.values():
            td.lock()
        return
        

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
    def has_errors(self):
        return len(self._error_strings) != 0

    def __repr__(self):
        return "{}:{}:{}:{}".format(self._parent, self._language, self._class_name, self._name)
