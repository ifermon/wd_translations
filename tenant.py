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

    def get_errors(self):
        ret_str = ""
        for to in self._trans_obj_dict.values():
            if not to.has_errors:
                continue
            ret_str += "{} has the following errors:\n".format(to)
            err_str = to.get_error_strings
            for err_type in err_str.keys():
                ret_str += "{}:\n".format(err_type)
                for err_msg in err_str[err_type]:
                    ret_str += "\terr_msg\n"
        return ret_str

    def put_trans_obj(self, trans_obj):
        self._trans_obj_dict[trans_obj.key] = trans_obj
        trans_obj.add_parent(self)
        return

    def remove_empty_translations(self):
        for key, to in self._trans_obj_dict.items():
            if to.has_translations:
                to.remove_untranslated_data()
            else:
                self._element.remove(to.element)
                del self._trans_obj_dict[key]
        return

    def get_translated_items(self):
        ret_list = []
        for to in self._trans_obj_dict.values():
            ret_list += to.get_translated_items()
        return ret_list

    def add_translation(self, translation):
        """
            This is called to add a translation, not during the "read-out" of the xml file,
            but during the moving of translations from one file to another

            This throws a KeyError if there is no matching item. Example: there is a ref id
            in the source tenant file that does not exist in the destination tenant file.

            The exception is passed upwards
            
            :param translation: this is a Trans_Data object that has a Translated or Rich Translated Value 
            :return: 
        """
        destination_trans_obj = self._trans_obj_dict[translation.parent_key]
        destination_trans_obj.update_translation(translation)
        #if self._update_hook:
        #    self._update_hook(self, translation)
        return

    def validate(self):
        for to in self._trans_obj_dict.values():
            to.get_inconsistent_translations()
        return

    def lock_translated_values(self):
        self._lock_translated_values = True
        for to in self._trans_obj_dict.values():
            to.lock_translated_values()
        return
        
    def register_updates(self, f_ptr):
        self._update_hook = f_ptr
        return

    def unregister_updates(self):
        self._update_hook = None
        return

    def get_all_items(self):
        ret_list = []
        for to in self._trans_obj_dict.values():
            ret_list += to.get_all_items()
        return ret_list

    def get_stats(self):
        num_trans_objects = len(self._trans_obj_dict)
        num_trans_data = 0
        num_WID_trans_data = 0
        num_translations = 0
        for td in self.get_all_items():
            num_trans_data += 1
            if td.is_WID:
                num_WID_trans_data += 1
            if td.has_translation:
                num_translations += 1
        return ("Name: {}\n\tNumber of classes: {}\n\tNumber of lines: {}"
                "\n\tNumber of translations: {}\n\tNumber of WID lines: {}").format(
                self.name, num_trans_objects, num_trans_data, num_translations, num_WID_trans_data)

    @property
    def name(self): return self._name
    @property
    def source_type(self): return self._source_type
    @property
    def tree(self): return self._tree
    @property
    def file_name(self): return self._file_name
    def __repr__(self): return self._name
