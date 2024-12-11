from os import environ as env


class classproperty(property):
    """
    A class property is a property that is shared by all instances of a class. This is useful for creating class-level
    properties that can be accessed without creating an instance of the class.

    Example Usage:
        >>> class MyClass:
        ...     @classproperty
        ...     def my_class_property(cls):
        ...         return 'Hello, world!'
        ...
        >>> MyClass.my_class_property
        'Hello, world!'
    """
    def __get__(self, obj, owner):
        return self.fget(owner)


class PrefixDescriptor:
    def __get__(self, obj, owner):
        if obj is None:
            return owner.DEFAULT_PREFIX

        return getattr(obj, '_prefix', owner.DEFAULT_PREFIX)

    def __set__(self, obj, value):
        obj._prefix = value
        
        
class DualActionProperty:
    def __init__(self, fget):
        self.fget = staticmethod(fget)
        
    def __get__(self, obj, owner):
        prefix = owner.prefix if obj is None else obj.prefix
        return self.fget.__func__(prefix, owner)

    def __set__(self, obj, value):
        prefix = obj.prefix
        env[f'{prefix}{self.fget.__func__.__name__.upper()}'] = value
