from __future__ import annotations
import typing
from typing import (
    Generator,
    Mapping,
    MutableMapping,
    Sequence,
    Union,
)

import dataclasses
import inspect
import math

import numpy as np
import astropy.units as u

from ...utils import make_collection, make_quantity


COORDINATE_TYPE_REGISTRY: dict[str, Coordinate] = {}


def identity_transformation(self: Coordinate) -> Coordinate:
    """
    [This docstring is AI-generated.]
    Identity transformation function.

    This function serves as the default transformation for coordinates. It returns the
    same coordinate without any transformation.

    Args:
        self (Coordinate): The input coordinate.

    Returns:
        Coordinate: The same input coordinate.
    """
    return self


@typing.dataclass_transform()
class CoordinateMeta(type):
    """
    [This docstring is AI-generated.]
    Metaclass for coordinate classes.

    This metaclass defines the behavior of coordinate classes and provides methods to
    handle coordinate transformations and other functionalities.

    Attributes:
        None
    """

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping, dtype: type = float):
        """
        [This docstring is AI-generated.]
        Create a new coordinate class.

        Parameters:
            metacls (type): The metaclass.
            name (str): The name of the new class.
            bases (tuple[type, ...]): The base classes of the new class.
            namespace (MutableMapping): The namespace of the new class.
            dtype (type, optional): The data type for coordinate values. Defaults to float.

        Returns:
            type: The newly created coordinate class.
        """
        units = namespace.get('__annotations__', {})
        axes = tuple(units.keys())
        namespace['__annotations__'] = {axis: dtype for axis in axes}
        namespace['units'] = units
        namespace['axes'] = axes
        namespace['__slots__'] = (*axes, 'shape')

        transforms_class = namespace.pop('Transforms', type('Transforms', (), {}))
        namespace['transforms'] = transforms = {
            name: identity_transformation
        }
        for attrname, attr in vars(transforms_class).items():
            if callable(attr):
                signature = inspect.signature(attr)
                if signature.return_annotation is signature.empty:
                    raise TypeError('Transformation functions require a return type annotation '
                                    '(to indicate what coordinate the method transforms to).')
                namespace[attrname] = attr
                transforms[signature.return_annotation] = attr

        def __post_init__(self):
            """
            [This docstring is AI-generated.]
            Post-initialization method for coordinate instances.

            This method sets up the coordinate instance after initialization, converting
            values to appropriate units and calculating the shape of the coordinate.

            Returns:
                None
            """
            for ax in self.axes:
                attr = getattr(self, ax)
                unit = self.units[ax]
                if isinstance(unit, str):
                    unit = eval(unit)
                attr = make_quantity(make_collection(attr), unit=unit)
                setattr(self, ax, attr)
            self.shape = tuple(getattr(self, axis).size for axis in self.axes)
        namespace['__post_init__'] = __post_init__

        cls = super().__new__(metacls, name, bases, namespace)

        # dataclass should be frozen too? currently freezing leads to bugs
        return dataclasses.dataclass(cls, eq=False, kw_only=True, repr=False)


class Coordinate(metaclass=CoordinateMeta):
    """
    [This docstring is AI-generated.]
    Base class for defining coordinate systems.

    This class serves as the foundation for creating coordinate classes. It provides
    methods and functionalities for coordinate transformations and handling.

    Attributes:
        None
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        [This docstring is AI-generated.]
        Initialize a subclass of Coordinate.

        This method is called when a new subclass of Coordinate is defined, and it
        registers the subclass in the COORDINATE_TYPE_REGISTRY.

        Returns:
            None
        """
        super().__init_subclass__(**kwargs)
        COORDINATE_TYPE_REGISTRY[cls.__name__] = cls

    def __repr__(self):
        body = []
        for ax in self.axes:
            quantity = getattr(self, ax)
            if len(quantity) == 1:
                body.append(
                    f'{quantity.value[0]} {quantity.unit}'
                )
            else:
                body.append(
                    f'{quantity.value} {quantity.unit}'
                )
        body = ', '.join(body)
        return f'{self.__class__.__name__}({body})'

    def __contains__(self, item: Union[Mapping, Sequence]) -> bool:
        """
        [This docstring is AI-generated.]
        Check if a point is contained within the coordinate.

        This method allows checking whether a point is contained within the coordinate,
        either as a Mapping or a Sequence.

        Parameters:
            item (Union[Mapping, Sequence]): The point to be checked.

        Returns:
            bool: True if the point is contained within the coordinate, False otherwise.

        Raises:
            NotImplementedError: If membership is tested on an unsupported type.
        """
        if isinstance(item, Mapping):
            return all(item[axis] in getattr(self, axis) for axis in self.axes)
        if isinstance(item, Sequence):
            return all(item[i] in getattr(self, axis) for i, axis in enumerate(self.axes))
        raise NotImplementedError('Membership can only be tested on Mapping or Sequence types.')

    def __len__(self) -> int:
        """
        [This docstring is AI-generated.]
        Get the total number of points in the coordinate.

        This method calculates and returns the total number of points present in the
        coordinate, considering all possible combinations of axis values.

        Returns:
            int: The total number of points in the coordinate.
        """
        return math.prod(self.shape)

    def __iter__(self) -> Generator[Coordinate, None, None]:
        """
        [This docstring is AI-generated.]
        Iterate over points in the coordinate.

        This method provides an iterator that yields all possible points in the
        coordinate, considering all combinations of axis values.

        Yields:
            Coordinate: An instance of the coordinate with different axis values.
        """
        for indices in np.ndindex(self.shape):
            coord = {axis: getattr(self, axis)[i] for i, axis in zip(indices, self.axes)}
            yield self.__class__(**coord)

    def __getitem__(self, ax: str) -> u.Quantity:
        """
        [This docstring is AI-generated.]
        Get the value of a specific axis in the coordinate.

        This method allows accessing the value of a specific axis in the coordinate.

        Parameters:
            ax (str): The axis for which to get the value.

        Returns:
            np.ndarray: The value of the specified axis.
        """
        return getattr(self, ax)

    def to(self, ctype: Coordinate) -> Coordinate:
        """
        [This docstring is AI-generated.]
        Convert the coordinate to a different coordinate type.

        This method allows converting the current coordinate to a different coordinate
        type. It uses registered transformation functions to perform the conversion.

        Parameters:
            ctype (Coordinate): The target coordinate type to convert to.

        Returns:
            Coordinate: The converted coordinate instance.

        Raises:
            TypeError: If the target coordinate type is not recognized or transformation is not available.
        """
        if ctype.__name__ not in COORDINATE_TYPE_REGISTRY:
            raise TypeError(f'Unrecognized coordinate type {ctype}')
        if ctype.__name__ not in self.transforms:
            available_transforms = ', '.join(self.transforms.keys())
            message = (f'Chained transformations/tree traversal is not implemented - '
                       f'available coordinate transformations from {self.__class__.__name__} '
                       f'are to {available_transforms}')
            raise NotImplementedError(message)
        return self.transforms[ctype.__name__](self)
