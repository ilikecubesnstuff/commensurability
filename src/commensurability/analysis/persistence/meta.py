import typing
from types import GenericAlias

import inspect
from abc import abstractstaticmethod
from collections.abc import Callable, MutableMapping

# depth = 0
# indent = '  '
# def debug_prints(f):
#     def inner(*args, **kwargs):
#         global depth
#         base = depth * indent
#         print(base, f'== {f.__name__} ==')
#         for arg in args:
#             print(base + indent, 'ARG', arg, type(arg))
#         for kw, arg in kwargs.items():
#             print(base + indent, 'KWARG', kw, '=', arg, type(arg))
#         depth += 1
#         result = f(*args, **kwargs)
#         depth -= 1
#         print(base + indent, 'RESULT', result, type(result))
#         print(base, '==')
#         return result
#     return inner

# @debug_prints
def recursive_subtype_check(__subtype, __type):
    """
    [This docstring is AI-generated.]
    Recursively checks if a given subtype is a valid subclass of a given type.

    This function determines whether the provided `__subtype` is a valid subclass
    of the provided `__type`. It supports checking complex type annotations,
    including generics, unions, and optionals, in a recursive manner.

    Args:
        __subtype: The potential subtype to be checked.
        __type: The reference type against which subtyping is evaluated.

    Returns:
        bool: Returns True if `__subtype` is a valid subclass of `__type`, and
        False otherwise.

    Note:
        This function is designed to handle various type annotations, including
        those from the `typing` module, such as Union and Optional. However, it may
        not fully support all types from the `typing` module and may raise
        NotImplementedError for unsupported or unimplemented types.

    Raises:
        NotImplementedError: If an unsupported or unimplemented type is encountered
        during the subtyping check.

    Example:
        # Check if a list of integers is a valid subclass of a list of numbers
        result = issubtype_recursive(list[int], list[float])
        # Returns False, since a list of integers is not a valid subclass of a list
        # of floats.
    """
    # if the base type is typing.Any, any subtype is valid
    if type(__type) is type(typing.Any):
        return True
    
    # deal with unsupported/unimplemented types
    if not isinstance(__type, type | GenericAlias):

        # hacked-in support for typing.Union and typing.Optional
        if type(__type) is type(typing.Union[int, float]):
            return any(
                recursive_subtype_check(__subtype, nth_parent_type)
                for nth_parent_type in typing.get_args(__type)
            )

        # conditional error messages
        if __type.__module__ == 'typing':
            raise NotImplementedError(f'Most typing module annotations are not supported, including {__type}')
        raise NotImplementedError(f'Unsupported type {__type}')

    # if subtype is not a type, it cannot be a subclass
    # returns False for type instances (not type subclasses)
    if not isinstance(__subtype, type | GenericAlias):
        return False

    # deal with non-generic-alias cases
    if isinstance(__type, type):

        # generic alias arguments are discarded for subclass checking
        if isinstance(__subtype, GenericAlias):
            return issubclass(typing.get_origin(__subtype), __type)
        return issubclass(__subtype, __type)

    # subtype of a generic alias must also be a generic alias
    if isinstance(__subtype, type):
        return False

    # compare (origin) type of generic aliases
    parent_origin = typing.get_origin(__type)
    sub_origin = typing.get_origin(__subtype)
    if not issubclass(sub_origin, parent_origin):
        return False

    # generic alias arguments must be of the same length
    parent_args = typing.get_args(__type)
    sub_args = typing.get_args(__subtype)
    if len(parent_args) != len(sub_args):
        return False

    # check subclassing on argument recursively
    return all(
        recursive_subtype_check(sub_arg, parent_arg)
        for sub_arg, parent_arg in zip(sub_args, parent_args)
    )


# TYPE_OR_ANNOTATION = type | GenericAlias | typing.Any








# class MesaMethods(type):

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         mesamethods = {}
#         for name, value in namespace.items():
#             if hasattr(value, '__ismesamethod__'):
#                 mesamethods[name] = value
#         for key in mesamethods:
#             del namespace[key]
#         namespace['__mesamethods__'] = mesamethods
#         return super().__new__(cls, name, bases, namespace)

#     def __call__(self, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         for name, value in self.__mesamethods__.items():
#             namespace[name] = value
#         return super().__call__(name, bases, namespace)


# def mesamethod(func):
#     func.__ismesamethod__ = True
#     return func


# class MesaMeta(type):

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         mesa = namespace.pop('Mesa', type('Mesa', (), {}))
#         namespace['Mesa'] = mesa
#         return super().__new__(cls, name, bases, namespace)

#     def __call__(self, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         for key, attr in vars(self.Mesa).items():
#             # print(key, getattr(attr, '__overwrite__', False))
#             if getattr(attr, '__overwrite__', False) or key not in namespace:
#                 # print('NEW KEY', key, attr)
#                 namespace[key] = attr
#         # print('CALL', namespace)
#         return super().__call__(name, bases, namespace)

# def overwrite(func):
#     func.__overwrite__ = True
#     return func


# class LatentTypeHierarchy(MesaMethods):

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         pass

#     def __call__(self, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         pass


# class BaseLTH(type, metaclass=LatentTypeHierarchy):

#     def __call__(self, obj):
#         lth_type = self.lth_type(obj)
#         cls = self[lth_type]
#         return type.__call__(cls, obj)

#     @abstractstaticmethod
#     def lth_type(obj: typing.Any):
#         pass

# class lth_on_callable_return(BaseLTH):

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         pass

#     @staticmethod
#     def lth_type(func: Callable):
#         if not isinstance(func, Callable):
#             raise TypeError('This object can only be constructed on callables')
#         return func.__annotations__.get('return', typing.Any)


# class serializer(metaclass=lth_on_callable_return):
    
#     def __class_getitem__(cls, key):
#         pass




class latent_type_hierarchy(type):

    def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
        if '__type__' not in namespace:
            namespace['__type__'] = typing.Any

        def __init__(self, obj):
            if not isinstance(obj, self.__class__):
                raise RuntimeError('Use the ".create" constructor to make an instance of this class')
            self.obj = obj
        namespace['__init__'] = __init__

        def __repr__(self):
            return f"<{self.__class__.__name__}[{self.__type__}] {self.obj}>"
        namespace['__repr__'] = __repr__

        def __class_getitem__(cls, key):
            new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
            new_cls.__type__ = key
            return new_cls
        namespace['__class_getitem__'] = __class_getitem__

        def __getattribute__(self, key):
            try:
                return object.__getattribute__(self, key)
            except AttributeError as e1:
                pass
            try:
                obj = object.__getattribute__(self, 'obj')
                return getattr(obj, key)
            except AttributeError as e2:
                raise AttributeError(e1)
        namespace['__getattribute__'] = __getattribute__

        def __call__(self, *args, **kwargs):
            return self.obj(*args, **kwargs)
        namespace['__call__'] = __call__

        return super().__new__(cls, name, bases, namespace)

    @abstractstaticmethod
    def __gettype__(func: Callable):
        pass

    def __repr__(self):
        return f"<{self.__name__}_type '{self.__type__}'>"

    def __subclasscheck__(self, __subclass: type) -> bool:
        associated_type = getattr(__subclass, '__type__', None)
        if not associated_type:
            return False
        return recursive_subtype_check(associated_type, self.__type__)

    def __instancecheck__(self, __instance: Callable) -> bool:
        if not isinstance(__instance, Callable):
            return False
        return self.__gettype__(__instance) == self.__type__


class serializer(latent_type_hierarchy):

    @classmethod
    def create(cls, func):
        namespace = {}
        namespace['__type__'] = cls.__gettype__(func)
        mesacls = cls(f'{cls.__name__}', (), namespace)
        inst = mesacls(func)
        return inst

    @staticmethod
    def __gettype__(func: Callable):
        return func.__annotations__.get('return', typing.Any)


class deserializer(latent_type_hierarchy):

    @classmethod
    def create(cls, func):
        namespace = {}
        namespace['__type__'] = cls.__gettype__(func)
        mesacls = cls(f'{cls.__name__}', (), namespace)
        inst = mesacls(func)
        return inst

    @staticmethod
    def __gettype__(func: Callable):
        signature = inspect.signature(func)
        items = tuple(
            param.annotation if param.annotation is not param.empty else typing.Any
            for param in signature.parameters.values()
        )
        return tuple[items]






# class serializer(type, metaclass=MesaMeta):

#     @classmethod
#     def create(metacls, func):
#         namespace = {}
#         namespace = {key: getattr(func, key) for key in dir(func.__class__)}
#         print(list(namespace.keys()))
#         # del namespace['__class__']
#         del namespace['__getattribute__']
#         namespace['__type__'] = metacls.__gettype__(func)
#         print(metacls)
#         cls = metacls(f'{metacls.__name__}_type', (), namespace)
#         print(cls)
#         # print(vars(cls))
#         print(dir(cls))
#         inst = cls(func)
#         print(inst, inst.obj)
#         print('repr check', inst.__repr__)
#         return inst

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         if '__type__' not in namespace:
#             namespace['__type__'] = typing.Any
#         return super().__new__(cls, name, bases, namespace)
    
#     def __call__(self, *args, **kwargs):
#         print('CALL INNER', self, args, kwargs)
#         return super().__call__(*args, **kwargs)

#     @staticmethod
#     def __gettype__(func: Callable):
#         return func.__annotations__.get('return', typing.Any)

#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"

#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)

#     def __instancecheck__(self, __instance: Callable) -> bool:
#         if not isinstance(__instance, Callable):
#             return False
#         return self.__gettype__(__instance) is self.__type__

#     class Mesa:
#         x = 1

#         @overwrite
#         def __init__(self, obj):
#             if not isinstance(obj, self.__class__):
#                 raise RuntimeError('Use the ".create" constructor to make an instance of this class')
#             self.obj = obj

#         @overwrite
#         def __repr__(self):
#             return f"{self.__class__.__name__}[{self.__type__}]({self.obj})"

#         def __class_getitem__(cls, key):
#             new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
#             new_cls.__type__ = key
#             return new_cls



# class deserializer(type, metaclass=MesaMeta):

#     @classmethod
#     def create(metacls, func):
#         namespace = {key: getattr(func, key) for key in dir(func)}
#         namespace['__type__'] = metacls.__gettype__(func)
#         cls = metacls(f'{metacls.__name__}_type', (), namespace)
#         inst = cls(func)
#         return inst

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         if '__type__' not in namespace:
#             namespace['__type__'] = typing.Any
#         return super().__new__(cls, name, bases, namespace)

#     @staticmethod
#     def __gettype__(func: Callable):
#         # print(func.__annotations__)
#         signature = inspect.signature(func)
#         # print(signature.parameters)
#         items = tuple(
#             param.annotation
#             for param in signature.parameters.values()
#             if param.annotation is not param.empty
#         )
#         __type__ = tuple[items]
#         return __type__

#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"

#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)

#     def __instancecheck__(self, __instance: Callable) -> bool:
#         if not isinstance(__instance, Callable):
#             return False
#         return self.__gettype__(__instance) is self.__type__

#     class Mesa:
#         x = 1

#         def __init__(self, obj):
#             if not isinstance(obj, self.__class__):
#                 raise RuntimeError('Use the ".create" constructor to make an instance of this class')
#             self.obj = obj

#         @overwrite
#         def __repr__(self):
#             return f"{self.__class__.__name__}[{self.__type__}]({self.obj})"

#         def __class_getitem__(cls, key):
#             new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
#             new_cls.__type__ = key
#             return new_cls















# class LatentTypeHierarchy(type, metaclass=MesaMethods):

#     def __new__(cls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         __type__ = namespace.get('__type__', typing.Any)
#         namespace['__type__'] = __type__

#         return super().__new__(cls, name, bases, namespace)

#     @abstractstaticmethod
#     def __gettype__(func: Callable):
#         pass

#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"

#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)

#     def __instancecheck__(self, __instance: Callable) -> bool:
#         if not isinstance(__instance, Callable):
#             return False
#         return self.__gettype__(__instance) is self.__type__

# class lth_on_callable_return(LatentTypeHierarchy):

#     @staticmethod
#     def __gettype__(func: Callable):
#         return func.__annotations__.get('return', typing.Any)
    
#     # @mesamethod
#     # def __call__(self, *args, **kwargs):
#     #     return self.obj(*args, **kwargs)


# class serializer(metaclass=lth_on_callable_return):
#     __type__ = typing.Any

#     @classmethod
#     def create(cls, func: Callable):
#         if not isinstance(func, Callable):
#             raise TypeError('This object can only be constructed using a callable')
#         # namespace = {key: getattr(func, key) for key in dir(func)}
#         namespace = {}
#         namespace |= vars(cls)
#         new_cls = type(cls.__name__, (cls,), namespace)
#         new_cls.__type__ = cls.__gettype__(func)
#         return new_cls(func)

#     def __init__(self, obj):
#         if not isinstance(obj, self.__class__):
#             raise RuntimeError('Use the ".create" constructor to make an instance of this class')
#         self.obj = obj

#     def __repr__(self):
#         return f"{self.__class__.__name__}[{self.__type__}]({self.obj})"

#     def __class_getitem__(cls, key):
#         new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
#         new_cls.__type__ = key
#         return new_cls























# class MetaMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         print('>> MetaMeta new', metacls, name, bases, namespace)
#         mesamethods = {}
#         for name, value in namespace.items():
#             if hasattr(value, '__ismesamethod__'):
#                 mesamethods[name] = value
#         for key in mesamethods:
#             del namespace[key]
#         namespace['__mesamethods__'] = mesamethods
#         print('NEW MESAMETHODS', mesamethods)
#         return super().__new__(metacls, name, bases, namespace)

#     def __call__(self, *args, **kwargs):
#         print('>> MetaMeta call', self, args, kwargs)
#         name, bases, namespace = args
#         for name, value in self.__mesamethods__.items():
#             print('MESAMETHODS', name, value)
#             namespace[name] = value
#         return super().__call__(*args, **kwargs)


# class DummyMeta(type, metaclass=MetaMeta):
#     pass

# class Meta(type, metaclass=MetaMeta):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         print('>> Meta new', metacls, name, bases, namespace)
#         return super().__new__(metacls, name, bases, namespace)

#     def __call__(self, *args, **kwargs):
#         print('>> Meta call', self, args, kwargs)
#         return super().__call__(*args, **kwargs)

#     @mesamethod
#     def test(self, x):
#         return x + 1


# class Dummy(metaclass=Meta):
#     pass

# class Base(metaclass=Meta):

#     def __new__(cls, *args, **kwargs):
#         print('>> Base new', cls, args, kwargs)
#         return super().__new__(cls, *args, **kwargs)

#     def __call__(self, *args, **kwargs):
#         print('>> Base call', self, args, kwargs)
#         return super().__call__(*args, **kwargs)


# inst = Base()
# print(inst.test(1))
# print(inst)
# print(inst())










































# class AttributeInitType(type):
#     def __call__(self, *args, **kwargs):
#         """Create a new instance."""

#         # First, create the object in the normal default way.
#         print(self, args, kwargs)
#         obj = type.__call__(self, *args)

#         # Additionally, set attributes on the new object.
#         for name, value in kwargs.items():
#             setattr(obj, name, value)

#         # Return the new object.
#         return obj

# class Car(object, metaclass=AttributeInitType):
#     @property
#     def description(self) -> str:
#         """Return a description of this car."""
#         return " ".join(str(value) for value in self.__dict__.values())

# new_car = Car(make='Toyota', model='Prius', year=2005, color='Green', engine='Hybrid')

# print(new_car)







# class InstanceMethodMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         instance_methods = {}
#         for name, value in namespace.items():
#             if hasattr(value, '__isinstancemethod__'):
#                 instance_methods[name] = value
#                 del namespace[name]
        
#         def __init_instance_methods__(self):
#             for name, value in instance_methods.items():
#                 setattr(self, name, value)
#         namespace['__init_instance_methods__'] = __init_instance_methods__
        
#         return super().__new__(metacls, name, bases, namespace)
    
#     def __call__(self, *args, **kwargs):
#         print(self, args, kwargs)
#         return type.__call__(self, *args, **kwargs)


# def instancemethod(func):
#     func.__isinstancemethod__ = True


# class Test(metaclass=InstanceMethodMeta):

#     @instancemethod
#     def f(self, x):
#         return x + 1



# class BaseLTH:
#     __type__ = None

#     @classmethod
#     def create(cls, obj):
#         __type__ = cls.lth__gettype__(obj)
#         return cls[__type__](obj)

#     def __init__(self, obj):
#         if self.lth__gettype__(obj) is not self.__type__:
#             raise RuntimeError('Use the ".create" constructor to make an instance of this class')
#         self.obj = obj

#     @abstractstaticmethod
#     def lth__gettype__(obj):
#         pass

#     def __repr__(self):
#         return f"{self.__class__.__name__}[{self.__type__}]({self.obj})"

#     def __class_getitem__(cls, key: Any):
#         new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
#         new_cls.__type__ = key
#         return new_cls















# class LatentTypeHierarchyMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         __type__ = namespace.get('__type__', Any)
#         namespace['__type__'] = __type__

#         for name in namespace:
#             if name.startswith('lth__'):
#                 method = namespace[name]
#                 namespace[name] = metacls.redefine_self(method)

#         return super().__new__(metacls, name, bases, namespace)

#     @staticmethod
#     def redefine_self(func):
#         def modified_method(self, *args, **kwargs):
#             print(self, args, kwargs)
#             return func(self.obj, *args, **kwargs)
#         return modified_method

#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"

#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)
    
#     def __instancecheck__(self, __instance: Any) -> bool:
#         if not hasattr(__instance, 'func'):
#             return False
#         associated_type = __instance.func.__annotations__['return']
#         return recursive_subtype_check(associated_type, self.__type__)


# class BaseLTH(metaclass=LatentTypeHierarchyMeta):
#     __type__ = None

#     @classmethod
#     def create(cls, obj):
#         __type__ = cls.lth__gettype__(obj)
#         return cls[__type__](obj)

#     def __init__(self, obj):
#         if self.lth__gettype__(obj) is not self.__type__:
#             raise RuntimeError('Use the ".create" constructor to make an instance of this class')
#         self.obj = obj

#     @abstractstaticmethod
#     def lth__gettype__(obj):
#         pass

#     def __repr__(self):
#         return f"{self.__class__.__name__}[{self.__type__}]({self.obj})"

#     def __class_getitem__(cls, key: Any):
#         new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
#         new_cls.__type__ = key
#         return new_cls


# class serializer(BaseLTH):

#     def lth__gettype__(obj):
#         return obj.__annotations__.get('return', typing.Any)






# class IndirectInstantiationMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         namespace.pop('__call__', None)
#         return super().__new__(metacls, name, bases, namespace)


# class LatentTypeHierarchyBaseMeta(type, metaclass=IndirectInstantiationMeta):
    
#     @abstractmethod
#     def __type__(obj: Any) -> TYPE_OR_ANNOTATION:
#         pass

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         associated_type = namespace.get('__type__', Any)
#         namespace['__type__'] = associated_type
        
#         def __repr__(self):
#             return f"{self.__class__.__name__}[{self.__type__}]({self.func})"
#         namespace['__repr__'] = __repr__

#         return super().__new__(metacls, name, bases, namespace)
# LTHBaseMeta = LatentTypeHierarchyBaseMeta


# class SerializerMeta(LTHBaseMeta):

#     def __type__(func: Callable) -> TYPE_OR_ANNOTATION:
#         return func.__annotations__.get('return', Any)
        
#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"
    
#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)
    
#     def __instancecheck__(self, __instance: Any) -> bool:
#         if not hasattr(__instance, 'func'):
#             return False
#         associated_type = __instance.func.__annotations__['return']
#         return recursive_subtype_check(associated_type, self.__type__)



# class GenericInheritanceMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         associated_type = namespace.get('__type__', Any)
#         namespace['__type__'] = associated_type

#         def __init__(self, func):
#             if func.__annotations__['return'] is not self.__type__:
#                 raise TypeError('Function return type must coincide with that of the Serializer class.')
#             self.func = func
#         namespace['__init__'] = __init__
        
#         def __repr__(self):
#             return f"{self.__class__.__name__}[{self.__type__}]({self.func})"
#         namespace['__repr__'] = __repr__

#         return super().__new__(metacls, name, bases, namespace)
        
#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"
    
#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)
    
#     def __instancecheck__(self, __instance: Any) -> bool:
#         if not hasattr(__instance, 'func'):
#             return False
#         associated_type = __instance.func.__annotations__['return']
#         return recursive_subtype_check(associated_type, self.__type__)


# class Serializer(metaclass=GenericInheritanceMeta):
#     __type__ = Any

#     def __init__(self, func):
#         if func.__annotations__['return'] is not self.__type__:
#             raise TypeError('Function return type must coincide with that of the Serializer class.')
#         self.func = func

#     def __call__(self, *args, **kwargs):
#         return self.func(*args, **kwargs)

#     def __class_getitem__(cls, key: Any):
#         new_serializer = type(cls.__name__, (cls,), dict(vars(cls)))
#         new_serializer.__type__ = key
#         return new_serializer


# def serializer(func: Callable):
#     associated_type = func.__annotations__.get('return', Any)
#     cls = Serializer[associated_type]
#     # print(cls(func))
#     return cls(func)


# class DeserializerMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         associated_type = namespace.get('__type__', Any)
#         namespace['__type__'] = associated_type

#         def __repr__(self):
#             return f"{self.__class__.__name__}[{self.__type__}]({self.func})"
#         namespace['__repr__'] = __repr__

#         return super().__new__(metacls, name, bases, namespace)
        
#     def __repr__(self):
#         return f"<{self.__name__} '{self.__type__}'>"
    
#     def __subclasscheck__(self, __subclass: type) -> bool:
#         associated_type = getattr(__subclass, '__type__', None)
#         if not associated_type:
#             return False
#         return recursive_subtype_check(associated_type, self.__type__)
    
#     def __instancecheck__(self, __instance: Any) -> bool:
#         if not hasattr(__instance, 'func'):
#             return False
#         associated_type = __instance.func.__annotations__['return']
#         return recursive_subtype_check(associated_type, self.__type__)


# class Deserializer(metaclass=DeserializerMeta):
#     __type__ = Any

#     def __init__(self, func):
#         if func.__code__.co_argcount < len(func.__code__.co_varnames):
#             raise TypeError('Function signature must only contain non-variadic positional arguments.\n'
#                             f'Function signature: {inspect.signature(func)}')
#         if func.__defaults__:
#             raise TypeError('Function signature must not contain any default values.\n'
#                             f'Function signature: {inspect.signature(func)}')
#         self.func = func

#     def __call__(self, *args, **kwargs):
#         return self.func(*args, **kwargs)

#     def __class_getitem__(cls, key: Any):
#         new_serializer = type(cls.__name__, (cls,), dict(vars(cls)))
#         new_serializer.__type__ = key
#         return new_serializer


# def deserializer(func: Callable):
#     associated_type = func.__annotations__.get('return', Any)
#     cls = Deserializer[associated_type]
#     # print(cls(func))
#     return cls(func)