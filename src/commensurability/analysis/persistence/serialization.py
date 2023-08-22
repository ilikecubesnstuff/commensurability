import inspect
import typing

from .meta import latent_type_hierarchy


class serializer(latent_type_hierarchy):
    """
    [This docstring is AI-generated.]
    A metaclass that facilitates the creation of serializer classes.
    Subclasses 'latent_type_hierarchy'.
    """

    @classmethod
    def create(cls, func: typing.Callable):
        """
        [This docstring is AI-generated.]
        Create a serializer instance for the given function.

        Args:
            func (typing.Callable): The function to be serialized.

        Returns:
            serializer: An instance of the serializer.
        """
        namespace = {}
        namespace['__type__'] = cls.__gettype__(func)
        mesacls = cls(f'{cls.__name__}', (object,), namespace)
        inst = mesacls(func)
        return inst

    @staticmethod
    def __gettype__(func: typing.Callable) -> typing.Any:
        """
        [This docstring is AI-generated.]
        Get the return type associated with a function.

        Args:
            func (typing.Callable): The function to extract the return type from.

        Returns:
            typing.Any: The return type of the function.
        """
        return func.__annotations__.get('return', typing.Any)


class deserializer(latent_type_hierarchy):
    """
    [This docstring is AI-generated.]
    A metaclass that facilitates the creation of deserializer classes.
    Subclasses 'latent_type_hierarchy'.
    """

    @classmethod
    def create(cls, func: typing.Callable):
        """
        [This docstring is AI-generated.]
        Create a deserializer instance for the given function.

        Args:
            func (typing.Callable): The function to be deserialized.

        Returns:
            deserializer: An instance of the deserializer.
        """
        namespace = {}
        namespace['__type__'] = cls.__gettype__(func)
        mesacls = cls(f'{cls.__name__}', (object,), namespace)
        inst = mesacls(func)
        return inst

    @staticmethod
    def __gettype__(func: typing.Callable) -> typing.Any:
        """
        [This docstring is AI-generated.]
        Get the parameter types as a tuple from a function's signature.

        Args:
            func (typing.Callable): The function to extract parameter types from.

        Returns:
            typing.Any: A tuple containing the parameter types.
        """
        signature = inspect.signature(func)
        items = tuple(
            param.annotation if param.annotation is not param.empty else typing.Any
            for param in signature.parameters.values()
        )
        return tuple[items]
