from __future__ import annotations
from collections.abc import (
    Mapping,
    Sequence
)
import typing

import dataclasses
import inspect
import math

import numpy as np
import astropy.units as u

from ...utils import make_collection, make_quantity


COORDINATE_TYPE_REGISTRY = {}


def identity_transformation(self):
    return self


@typing.dataclass_transform()
class CoordinateMeta(type):

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: typing.MutableMapping, dtype: type = float):
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
            for ax in self.axes:
                attr = getattr(self, ax)
                unit = self.units[ax]
                if isinstance(unit, str):
                    unit = eval(unit)
                attr = make_quantity(make_collection(attr, cls=tuple), unit=unit)
                setattr(self, ax, attr)
            self.shape = tuple(getattr(self, axis).size for axis in self.axes)
        namespace['__post_init__'] = __post_init__

        cls = super().__new__(metacls, name, bases, namespace)
        return dataclasses.dataclass(cls, eq=False, kw_only=True)  # should be frozen too? currently freezing leads to bugs


class Coordinate(metaclass=CoordinateMeta):
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        COORDINATE_TYPE_REGISTRY[cls.__name__] = cls

    def __contains__(self, item: typing.Union[Mapping, Sequence]):
        if isinstance(item, Mapping):
            return all(item[axis] in getattr(self, axis) for axis in self.axes)
        if isinstance(item, Sequence):
            return all(item[i] in getattr(self, axis) for i, axis in enumerate(self.axes))
        raise NotImplementedError('Membership can only be tested on Mapping or Sequence types.')

    def __len__(self):
        return math.prod(self.shape)

    def __iter__(self):
        for indices in np.ndindex(self.shape):
            coord = {axis: getattr(self, axis)[i] for i, axis in zip(indices, self.axes)}
            yield self.__class__(**coord)

    def __getitem__(self, ax: str):
        return getattr(self, ax)

    def to(self, ctype: 'Coordinate') -> 'Coordinate':
        if ctype.__name__ not in COORDINATE_TYPE_REGISTRY:
            raise TypeError(f'Unrecognized coordinate type {ctype}')
        if ctype.__name__ not in self.transforms:
            available_transforms = ', '.join(self.transforms.keys())
            message = (f'Chained transformations/tree traversal is not implemented - '
                       f'available coordinate transformations from {self.__class__.__name__} '
                       f'are to {available_transforms}')
            raise NotImplementedError(message)
        return self.transforms[ctype.__name__](self)
