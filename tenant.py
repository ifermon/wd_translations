from __init__ import *
"""
    The tenant that the data is sourced from

"""

class Tenant(object):

    def __init__(self, name, tree, source_type=XML):
        self._name = name
        self._source_type = source_type
        self._tree = tree
        self._element = tree.getroot()
        self._trans_obj_dict = {}
        return

    def put_trans_obj(self, trans_obj):
        self._trans_obj_dict[trans_obj.key] = trans_obj
        trans_obj.add_parent(self)
        return

    def remove_empty_translations(self):
        for to in self._trans_obj_dict.values():
            if to.has_translations:
                to.remove_untranslated_data()
            else:
                self._element.remove(to.element)
        return

    def get_translated_items(self):
        ret_list = []
        for to in self._trans_obj_dict.values():
            ret_list += to.get_translated_items()
        return ret_list

    def add_translation(self, translation):
        self._trans_obj_dict[translation.parent_key].update_translation(translation)
        return

    def validate(self):
        for to in self._trans_obj_dict.values():
            to.get_inconsistent_translations()
        return
        
    @property
    def name(self): return self._name
    @property
    def source_type(self): return self._source_type
    @property
    def tree(self): return self._tree
