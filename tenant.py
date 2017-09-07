from __init__ import *
"""
    The tenant that the data is sourced from

"""

class Tenant(object):

    def __init__(self, name, tree, file_name, source_type=XML):
        self._name = name
        self._source_type = source_type
        self._tree = tree
        self._update_hook = None
        self._file_name = file_name
        self._element = tree.getroot()
        self._trans_obj_dict = {}
        self._lock_translated_values = False
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
        destination_item = self._trans_obj_dict[translation.parent_key]
        if not self._lock_translated_values or not destination_item.has_translation:
            destination_item.update_translation(translation)
            if self._update_hook:
                self._update_hook(self, translation)
        return

    def validate(self):
        for to in self._trans_obj_dict.values():
            to.get_inconsistent_translations()
        return

    def lock_translated_values(self):
        self._lock_translated_values = True
        return
        
    def register_updates(self, f_ptr):
        self._update_hook = f_ptr
        return

    def unregister_updates(self):
        self._update_hook = None
        return

    @property
    def name(self): return self._name
    @property
    def source_type(self): return self._source_type
    @property
    def tree(self): return self._tree
    @property
    def file_name(self): return self._file_name
