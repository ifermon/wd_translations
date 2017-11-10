from weakref import WeakValueDictionary

class Translated_Class(object):
    """
        For user generated (not WD generated) translation files
    """

    def __new__(cls, *args, **kwargs):
        """
            Only one instance per class_name - keep a class level list of instances and only create a new one if
            this is a new class name
        :param args:
        :param kwargs:
        :return:
        """
        if "class_names" not in cls.__dict__:
            cls.class_names = WeakValueDictionary()
        class_name = args[0]
        if class_name not in cls.class_names:
            #instance = object.__new__(cls, *args, **kwargs)
            instance = object.__new__(cls)
            cls.class_names[class_name] = instance
        else:
            instance = cls.class_names[class_name]
        return instance

    def __init__(self, class_name, name):
        """
        :param class_name:
        :param name:
        """
        self._class_name = class_name
        self._name = name
        self._key = (class_name, name)
        self._item_list = []
        self._key_dict = {}
        return

    def add_translatable_item(self, titem):
        assert type(titem)==Translatable_Item, "Invalid item passed to add_item"
        self._item_list.append(titem)
        titem.set_parent(self)
        self._key_dict[titem.key] = titem
        return

    def get_translatable_item_by_key(self, key):
        if key in self._key_dict:
            ret = self._key_dict[key]
        else:
            ret = None
        return ret

    @property
    def key(self): return self._key
    @property
    def class_name(self): return self._class_name
    @property
    def name(self): return self._name

    def next_item(self): yield from self._item_list

class Translatable_Item(object):
    def __init__(self, reference_type, reference_id, base_value, rich_flag):
        self._reference_type = reference_type
        self._reference_id = reference_id
        self._base_value = base_value
        assert type(rich_flag)==bool, "Invalid boolean type passed to Translatable Item"
        self._rich_flag = rich_flag
        self._translations = []
        self._parent = None
        self._match_found = False
        if reference_type == "WID":
            self._key = u"{}{}".format(reference_type, base_value)
        else:
            self._key = u"{}{}{}".format(reference_type, reference_id, base_value)
        return

    def get_translated_value(self, lang):
        ret = None
        for t in self._translations:
            if t.lang == lang:
                ret = t.trans_text
        return ret

    def add_translation(self, trans):
        assert type(trans)==Translation, "Invalid Translation type passed to add translation"
        self._translations.append(trans)
        trans.set_parent(self)
        return

    def found_match(self): self._match_found = True
    @property
    def is_matched(self): return self._match_found
    def set_parent(self, parent):
        self._parent = parent
    @property
    def key(self): return self._key
    @property
    def reference_type(self): return self._reference_type
    @property
    def reference_id(self): return self._reference_id
    @property
    def base_value(self): return self._base_value
    @property
    def rich_flag(self): return self._rich_flag

    def next_translation(self): yield from self._translations

class Translation(object):
    def __init__(self, lang, trans_text):
        self._lang = lang
        self._trans_text = trans_text
        self._parent = None
        return

    @property
    def lang(self): return self._lang
    @property
    def trans_text(self): return self._trans_text

    def set_parent(self, parent):
        self._parent = parent


