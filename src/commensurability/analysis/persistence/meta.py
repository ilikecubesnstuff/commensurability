from __future__ import annotations

from abc import abstractstaticmethod
from types import GenericAlias
import typing


ANY_TYPE = type(typing.Any)
UNION_TYPE = type(typing.Union[int, float])


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
    if type(__type) is ANY_TYPE:
        return True

    # deal with unsupported/unimplemented types
    if not isinstance(__type, type | GenericAlias):

        # hacked-in support for typing.Union and typing.Optional
        if type(__type) is UNION_TYPE:
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


class latent_type_hierarchy(type):
    """
    [This docstring is AI-generated.]
    A metaclass that enables the creation of classes with latent type hierarchies.
    """

    def __new__(cls, name: str, bases: tuple[type, ...], namespace: typing.MutableMapping) -> 'latent_type_hierarchy':
        """
        [This docstring is AI-generated.]
        Create a new class with the specified name, base classes, and namespace.

        Args:
            name (str): The name of the new class.
            bases (tuple[type, ...]): Tuple of base classes for the new class.
            namespace (typing.MutableMapping): The namespace containing class attributes and methods.

        Returns:
            latent_type_hierarchy: The newly created class.

        Note:
            If '__type__' is not defined in the namespace, it is set to 'typing.Any'.
        """

        if '__type__' not in namespace:
            namespace['__type__'] = typing.Any

        def __init__(self, _obj: typing.Any):
            """
            [This docstring is AI-generated.]
            Initialize an instance of the latent type class.

            Args:
                _obj (typing.Any): The object to associate with the instance.

            Raises:
                RuntimeError: If the object is not a valid instance of the class.
            """
            if not isinstance(_obj, self.__class__):
                raise RuntimeError('Use the ".create" constructor to make an instance of this class')
            self._obj = _obj
        namespace['__init__'] = __init__

        def __repr__(self) -> str:
            """
            [This docstring is AI-generated.]
            Return a string representation of the instance.

            Returns:
                str: The string representation.
            """
            return f"<{self.__class__.__name__}[{self.__type__}] {self._obj}>"
        namespace['__repr__'] = __repr__

        def __class_getitem__(cls, key: typing.Any) -> 'latent_type_hierarchy':
            """
            [This docstring is AI-generated.]
            Get an instance of the class with a specific associated type.

            Args:
                key (typing.Any): The associated type for the new instance.

            Returns:
                latent_type_hierarchy: A new class instance associated with the specified type.
            """
            new_cls = type(cls.__name__, (cls,), dict(vars(cls)))
            new_cls.__type__ = key
            return new_cls
        namespace['__class_getitem__'] = __class_getitem__

        def __getattribute__(self, key: str) -> typing.Any:
            """
            [This docstring is AI-generated.]
            Get the attribute or method from the instance or the associated object.

            Args:
                key (str): The attribute or method name.

            Returns:
                typing.Any: The value of the attribute or the result of the method.
            """
            try:
                return object.__getattribute__(self, key)
            except AttributeError as e1:
                try:
                    _obj = object.__getattribute__(self, '_obj')
                    return getattr(_obj, key)
                except AttributeError:
                    raise AttributeError(e1)
        namespace['__getattribute__'] = __getattribute__

        def __call__(self, *args, **kwargs) -> typing.Any:
            """
            [This docstring is AI-generated.]
            Call the associated object with the specified arguments and keyword arguments.

            Returns:
                typing.Any: The result of the function call.
            """
            return self._obj(*args, **kwargs)
        namespace['__call__'] = __call__

        return super().__new__(cls, name, bases, namespace)

    @abstractstaticmethod
    def __gettype__(obj: typing.Any) -> typing.Any:
        """
        [This docstring is AI-generated.]
        Get the type associated with an object.

        Args:
            obj (typing.Any): The object for which to determine the associated type.

        Returns:
            typing.Any: The associated type.
        """
        pass

    def __repr__(self) -> str:
        """
        [This docstring is AI-generated.]
        Return a string representation of the metaclass instance.

        Returns:
            str: The string representation.
        """
        return f"<{self.__name__}_type '{self.__type__}'>"

    def __subclasscheck__(self, __subclass: type) -> bool:
        """
        [This docstring is AI-generated.]
        Check if a class is a subclass, considering the associated types.

        Args:
            __subclass (type): The class to check.

        Returns:
            bool: True if the class is a subclass, False otherwise.
        """
        associated_type = getattr(__subclass, '__type__', None)
        if not associated_type:
            return False
        return recursive_subtype_check(associated_type, self.__type__)

    def __instancecheck__(self, __instance: typing.Callable) -> bool:
        """
        [This docstring is AI-generated.]
        Check if an object is an instance of the associated type.

        Args:
            __instance (typing.Callable): The object to check.

        Returns:
            bool: True if the object is an instance of the associated type, False otherwise.
        """
        if issubclass(type(__instance), self):
            __instance = __instance._obj
        if not isinstance(__instance, typing.Callable):
            return False
        return self.__gettype__(__instance) == self.__type__
