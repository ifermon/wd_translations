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


    def remove_untranslated_data(self):
        for d in self._trans_data_dict.values():
            if not d.has_translation:
                self._element.remove(d.element)
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
        

    @property
    def key(self):
        return self._key
    @property
    def parent(self):
        return self._parent
    @property
    def language(self):
        return self._language
    @property
    def class_name(self):
        return self._class_name
    @property
    def name(self):
        return self._name
    @property
    def namespace(self):
        return self._namespace
    @property
    def element(self):
        return self._element
    @property
    def has_translations(self):
        return self._has_translations
