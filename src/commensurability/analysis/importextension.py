from __future__ import annotations

import inspect
import textwrap
import typing


def _unavailable(e: Exception):
    """
    [This docstring is AI-generated.]
    A utility function to create a placeholder class that raises the provided exception.

    Parameters:
        e (Exception): The exception to be raised.

    Returns:
        class: A dynamically created class that raises the given exception upon instantiation.
    """
    class Unavailable:
        """
        [This docstring is AI-generated.]
        Placeholder class that raises the provided exception upon instantiation.
        """
        def __init__(self):
            raise e
    return Unavailable


class ExtendImportsMeta(type):
    """
    [This docstring is AI-generated.][Modified]
    A metaclass that dynamically extends classes with additional imports.

    This metaclass allows classes to extend their functionality by providing extra imports
    that might not be present in the environment. It attempts to import the specified
    imports and injects them into the class's namespace, enabling the class to use them.
    If any import fails, the class becomes unavailable and raises an exception.

    Usage:
        class MyClass(ExtendImports):
            def __imports__():
                # my_additional_imports
                ...

    Attributes:
        None
    """
    def __imports__():
        """
        [This docstring is AI-generated.]
        Placeholder method to define additional imports for a class.

        This method should be overridden in the class using the metaclass to provide
        the required additional imports.

        Returns:
            None
        """
        pass

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: typing.MutableMapping):
        """
        [This docstring is AI-generated.]
        Create a new class with dynamically injected imports.

        Parameters:
            metacls (type): The metaclass.
            name (str): The name of the new class.
            bases (tuple[type, ...]): The base classes of the new class.
            namespace (typing.MutableMapping): The namespace of the new class.

        Returns:
            type: The newly created class with injected imports or a placeholder if imports fail.
        """
        imports = namespace.pop('__imports__', metacls.__imports__)
        src = inspect.getsource(imports)
        *_, body = src.partition('\n')
        try:
            exec(textwrap.dedent(body), {}, namespace)
        except ModuleNotFoundError as e:
            return _unavailable(e)
        return super().__new__(metacls, name, bases, namespace)


class ExtendImports(metaclass=ExtendImportsMeta):
    """
    [This docstring is AI-generated.][Modified]
    A base class that allows extending functionality with additional imports.

    This class serves as a base for other classes that need to dynamically extend their
    functionality with extra imports. The '__imports__' method should be defined in
    subclasses to provide the required additional imports.

    Attributes:
        None
    """
    pass
