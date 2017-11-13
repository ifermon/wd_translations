from collections import defaultdict
from .__init__ import debug

class Base(object):
    def delete(self): pass

class Indexable(Base):
    def _add_to_index(self, queue_name, key):
        cls = type(self)
        if "_list_of_indicies" not in cls.__dict__:
            setattr(cls, "_list_of_indicies", set())
        if queue_name not in cls.__dict__:
            setattr(cls, queue_name, defaultdict(list))
            cls._list_of_indicies.add(queue_name)
        getattr(cls, queue_name)[key].append(self)
        return

    def delete(self):
        cls = type(self)
        for index_name in cls._list_of_indicies:
            d = getattr(cls, index_name)
            for k, v in d.items():
                if v is self:
                    del d[k]
        super().delete()
        return

class Upsert(Base):
    """
        This object lets inheriting objects "upsert" insert if not exists, otherwise update
        Requires inheriting object to define the method generate_key.
        When a new object is created, if an object with matching key value already esists, then that matching
        object is returned (no new object created). Otherwise a new object with key value is created.

        This object also defines a method for adding an index - a dict indexed by key and containing a list of items
        having that key (e.g. if you define a key for "color" it will return all items with color blue)
    """
    def __new__(cls, *args, **kwargs):
        """
        """
        if "dict" not in cls.__dict__:
            cls.dict = {}
        key = cls.generate_key(*args)
        if key not in cls.dict:
            instance = object.__new__(cls)
            instance._first_time_in_init = True
            instance._key = key
            cls.dict[key] = instance
        else:
            instance = cls.dict[key]
        return instance

    def delete(self):
        # Clean up dict reference
        cls = type(self)
        del cls.dict[self.key]
        super().delete()
        return

    @classmethod
    def generate_key(cls, *args): # This must always be defined by the inheriting class
        assert False, "Method generate_key must be defined for cls {}".format(cls)

class Indexable_Upsert(Upsert, Indexable):
    def _delete(self):
        print("In indexable upsert del")
        super()._delete()  # Call both
        return

class Translatable_Class(Indexable_Upsert):
    @classmethod
    def generate_key(cls, *args):
        class_name = args[0]
        name = args[1]
        return (class_name, name)

    def __init__(self, class_name, name):
        if self._first_time_in_init:
            self._first_time_in_init = False
            self._class_name = class_name
            self._name = name
            self._my_translatable_items = []
            self._has_translations = False
        return

    def set_has_translations(self): self._has_translations = True

    @property
    def has_translations(self): return self._has_translations
    @property
    def class_name(self): return self._class_name
    @property
    def name(self): return self._name

    def add_translatable_item(self, translatable_item):
        assert type(translatable_item) == Translatable_Item, "Invalid type passed to add_translatable_item"
        self._my_translatable_items.append(translatable_item)
        return

class Translatable_Item(Indexable_Upsert):
    @classmethod
    def generate_key(cls, *args):
        class_name = args[0]
        name = args[1]
        ref_id_type = args[2]
        ref_id = args[3]
        parent_ref_id_type = args[4]
        parent_ref_id = args[5]
        base_value = args[6]
        rich_base_value = args[7]
        # Use ref_id if it's not a WID. Otherwise use value if it exists, finally use rich base value
        if ref_id_type == "WID":
            ref_id_type = None
            ref_id = None
        if parent_ref_id_type == "WID":
            parent_ref_id = None
            parent_ref_id_type = None
        if not ref_id_type and not parent_ref_id_type:
            # We need to use the translated value as part of the key
            if not base_value:
                value = rich_base_value
            else:
                value = base_value
        else:
            value = (ref_id_type, ref_id, parent_ref_id_type, parent_ref_id)
        if not value:
            raise KeyError  # This should never happen, we should always have either value or base value
        return (class_name, name, value)

    def __init__(self, class_name, name, ref_id_type, ref_id, parent_ref_id_type, parent_ref_id,
                 base_value, rich_base_value, source_name_or_obj, language=None,
                 translated_value=None, rich_translated_value=None, namespace=None ):
        # We may already exist, so check to see if we are already defined
        if self._first_time_in_init:
            debug("Creating new translatable item with key {}".format(self._key))
            self._first_time_in_init = False
            self._translated_class = Translatable_Class(class_name, name)
            self._translated_class.add_translatable_item(self)
            self._class_name = class_name
            self._name = name
            self._base_value = base_value
            self._rich_base_value = rich_base_value
            self._my_sources = set()
            self._my_source_keys = {}
            self._my_translations = []
            self._add_to_index("by_class_and_name", (class_name, name))
            self._namespace = namespace
        if namespace:
            self._namespace = namespace
        if type(source_name_or_obj) == str:
            source = Translation_Source(source_name_or_obj, self)
        elif type(source_name_or_obj) == Translation_Source:
            source = source_name_or_obj
        self._add_to_index("by_source_class_name_and_name", (source, class_name, name))
        self.add_source(source)
        self.add_source_key(source, ref_id_type, ref_id, parent_ref_id_type, parent_ref_id)
        self.add_translation(source, language, translated_value, rich_translated_value)
        return

    def add_source_key(self, source, ref_id_type, ref_id, parent_ref_id_type, parent_ref_id):
        assert type(source) == Translation_Source, "Invalid source type passed to add source key"
        self._my_source_keys[source] = Translatable_Item_Translation_Source_Key(source, self, ref_id_type, ref_id, parent_ref_id_type, parent_ref_id)
        return

    def add_source(self, source):
        assert type(source) == Translation_Source, "Invalid source type passed to add_source {}".format(type(source))
        self._my_sources.add(source)
        return

    def get_translatable_item_source_key(self, source): return self._my_source_keys[source]

    @property
    def rich_base_value(self): return self._rich_base_value
    @property
    def base_value(self): return self._base_value
    @property
    def namespace(self): return self._namespace
    @property
    def class_name(self): return self._class_name
    @property
    def name(self): return self._name
    @property
    def key(self): return self._key
    @property
    def has_translation(self): return bool(self._my_translations)

    def add_translation(self, source, language, translated_value, rich_translated_value):
        if translated_value or rich_translated_value:
            source_language_translated_value = Source_Language_Translated_Value(source, language, translated_value, rich_translated_value, self)
            self._my_translations.append(source_language_translated_value)
            self._translated_class.set_has_translations()
        return

    def __repr__(self): return "Translatable Item: Class <{}> Name <{}> Base Value <{}> Rich Base Value <{}>".format(
            self._class_name, self._name, self._base_value, self._rich_base_value )

class Translatable_Item_Translation_Source_Key(object):
    """ For WID based translatable items we need to keep the specific source key """
    def __init__(self, source, translatable_item, ref_id_type, ref_id, parent_ref_id_type, parent_ref_id):
        assert type(source) == Translation_Source, "Invavlid source type passed to Translatable Item Source Key init {}".format(type(source))
        assert type(translatable_item) == Translatable_Item, "Invavlid translatable item type passed to Translatable Item Source Key init {}".format(type(translatable_item))
        self._source = source
        self._translatable_item = translatable_item
        self._ref_id_type = ref_id_type
        self._ref_id = ref_id
        self._parent_ref_id_type = parent_ref_id_type
        self._parent_ref_id = parent_ref_id
        self._my_source_language_translated_values = []
        return

    @property
    def parent_ref_id_type(self): return self._parent_ref_id_type
    @property
    def parent_ref_id(self): return self._parent_ref_id
    @property
    def ref_id_type(self): return self._ref_id_type
    @property
    def ref_id(self): return self._ref_id

    def add_source_language_translated_value(self, source_language_translated_value):
        self._my_source_language_translated_values.append(source_language_translated_value)
        return

class Translation_Source(Indexable_Upsert):
    @classmethod
    def generate_key(cls, *args):
        source_name = args[0]
        return source_name

    def __init__(self, source_name, translatable_item=None):
        assert type(source_name) == str, "Invalid type passed for source name {}".format(type(source_name))
        if self._first_time_in_init:
            debug("New source named {}".format(source_name))
            self._first_time_in_init = False
            self._source_name = source_name
            self._my_translatable_items = []
            self._my_source_language_translated_values = []
            self._namespace = None
        if translatable_item:
            assert type(translatable_item) == Translatable_Item, "Invalid type passed for translatable item {}".format(type(translation))
            self._my_translatable_items.append(translatable_item)
        return

    def set_namespace(self, namespace):
        self._namespace = namespace

    def add_source_language_translated_value(self, source_language_translated_value):
        self._my_source_language_translated_values.append(source_language_translated_value)
        return

    def add_translatable_item(self, translatable_item):
        self._my_translatable_items.append(translatable_item)
        return

    @property
    def namespace(self): return self._namespace
    @property
    def has_translated_values(self): return bool(self._my_source_language_translated_values)

class Source_Language_Translated_Value(Indexable):
    def __init__(self, source, language, translated_value, rich_translated_value, parent):
        assert type(source) == Translation_Source, "Invalid type passed for source {}".format(type(source))
        assert type(parent) == Translatable_Item, "Invaid type passed for parent {}".format(type(parent))
        self._source = source
        source.add_source_language_translated_value(self)
        self._language = language
        self._translated_value = translated_value
        self._rich_translated_value = rich_translated_value
        self._parent = parent
        self._add_to_index("by_language_class_name_name_and_source", (language, parent.class_name, parent.name, source))
        return

    def has_source(self, source): return source in self._parent._my_sources

    @property
    def rich_translated_value(self): return self._rich_translated_value
    @property
    def translated_value(self): return self._translated_value
    @property
    def rich_base_value(self): return self._parent.rich_base_value
    @property
    def base_value(self): return self._parent.base_value
    @property
    def parent(self): return self._parent

    def ref_id(self, source):
        assert type(source) == Translation_Source, "Invalid source type passed"
        return self._parent.get_translatable_item_source_key(source).ref_id

    def ref_id_type(self, source):
        assert type(source) == Translation_Source, "Invalid source type passed"
        return self._parent.get_translatable_item_source_key(source).ref_id_type

    def parent_ref_id(self, source):
        assert type(source) == Translation_Source, "Invalid source type passed"
        return self._parent.get_translatable_item_source_key(source).parent_ref_id

    def parent_ref_id_type(self, source):
        assert type(source) == Translation_Source, "Invalid source type passed"
        return self._parent.get_translatable_item_source_key(source).parent_ref_id_type

if __name__ == "__main__":
    # Some simple tests
    a = Translatable_Item("a class name", "name", "ref id type", "ref id", "parent ref id type", "parent ref id", "base value", "rich base value")
    b = Translatable_Item("a class name", "name", "ref id type", "ref id", "parent ref id type", "parent ref id", "base value", "rich base value")
    c = Translatable_Item("c class name", "name", "ref id type", "ref id", "parent ref id type", "parent ref id", "base value", "rich base value")

    print(a is b)
