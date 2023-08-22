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



class Cartesian(Coordinate):
    x: u.kpc
    y: u.kpc
    z: u.kpc
    vx: u.km / u.s
    vy: u.km / u.s
    vz: u.km / u.s

    class Transforms:
        def to_cylindrical(self) -> Cylindrical:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            R = np.sqrt(self.x ** 2 + self.y ** 2)
            phi = np.arctan2(self.y, self.x)
            vR = (self.x * self.vx + self.y * self.vy)/R
            vT = (-self.y * self.vx + self.x * self.vy)/R
            return Cylindrical(R=R, vR=vR, vT=vT, z=self.z, vz=self.vz, phi=phi)


class Cylindrical(Coordinate):
    R: u.kpc
    vR: u.km / u.s
    vT: u.km / u.s
    z: u.kpc
    vz: u.km / u.s
    phi: u.deg

    class Transforms:
        def to_cartesian(self) -> Cartesian:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            x = self.R * np.cos(self.phi)
            y = self.R * np.sin(self.phi)

            vx = self.vR * np.cos(self.phi) - self.vT * np.sin(self.phi)
            vy = self.vT * np.cos(self.phi) + self.vR * np.sin(self.phi)

            return Cartesian(x=x, y=y, z=self.z, vx=vx, vy=vy, vz=self.vz)

Y: Coordinate
class X(Coordinate):
    x: u.kpc
    y: u.kpc

    class Transforms:
        def to_y(self) -> Y:
            print('transform X -> Y')
            pass


class Y(Coordinate):
    x: u.kpc
    y: u.kpc

    class Transforms:
        def to_x(self) -> X:
            print('transform Y -> X')
            pass



# class CoordinateCollectionMeta(type):

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping, dtype: type = float):
#         axes = namespace.get('__annotations__', {})
#         namespace['axes'] = tuple(axes.keys())

#         transforms_class = namespace.get('Transforms', type('Transforms', (), {}))
#         namespace['transforms'] = transforms = {
#             name: (lambda self: self)
#         }
#         for attr, obj in vars(transforms_class).items():
#             if callable(obj):
#                 namespace[attr] = obj
#                 transforms[obj.__annotations__['return']] = obj
#         namespace.pop('Transforms', None)

#         init_params = ', '.join(f'{axis}: {dtype.__name__}' for axis in axes)
#         init_body = '\n'.join((
#             f'    {axis} = make_collection({axis})\n'
#             f'    {axis} = make_quantity({axis}, unit=u.Unit("{str(unit).replace("u.", "")}"))\n'
#             f'    self.{axis} = {axis}\n'
#         ) for axis, unit in axes.items())
#         repr_body = f'{name}Coordinates({{", ".join(f"{{axis}}={{getattr(self, axis)}}" for axis in self.axes)}})'
#         body = (
#             f'def __init__(self, {init_params}):\n'
#             f'{init_body}\n'
#             f'    self.shape = tuple(getattr(self, axis).size for axis in self.axes)\n'
#             f'    self.Coordinate = make_dataclass(f"{name}Coordinate", self.axes, bases=(Coordinate,))\n'
#             f'\n'
#             f'def __repr__(self):\n'
#             f'    return f\'{repr_body}\'\n'
#         )
#         # print(body)
#         exec(body, globals(), namespace)
#         return super().__new__(metacls, name, bases, namespace)


# class CoordinateCollection(metaclass=CoordinateCollectionMeta):
#     class Coordinate:
#         pass
#     type_registry = {}

#     def __init_subclass__(cls, **kwargs) -> None:
#         super().__init_subclass__(**kwargs)
#         CoordinateCollection.type_registry[cls.__name__] = cls

#     def __contains__(self, item: Union[Mapping, Sequence]):
#         if isinstance(item, Mapping):
#             return all(item[axis] in getattr(self, axis) for axis in self.axes)
#         if isinstance(item, Sequence):
#             return all(item[i] in getattr(self, axis) for i, axis in enumerate(self.axes))
#         raise NotImplementedError('Membership can only be tested on Mapping or Sequence types.')

#     def __len__(self):
#         return prod(self.shape)

#     def __iter__(self):
#         for indices in np.ndindex(self.shape):
#             coord = {axis: getattr(self, axis)[i] for i, axis in zip(indices, self.axes)}
#             # coord['type'] = self.__class__.__name__
#             yield self.Coordinate(**coord)

#     def __getitem__(self, ax: str):
#         return getattr(self, ax)
    
#     def __save__(self):
#         return [], {axis: self[axis] for axis in self.axes}

#     @classmethod
#     def __read__(cls, file):
#         params = {axis: file.attrs[axis] for axis in cls.axes}
#         return cls(**params)

#     def to(self, ctype: CoordinateCollection) -> CoordinateCollection:
#         if ctype.__name__ not in CoordinateCollection.type_registry:
#             raise TypeError(f'Unrecognized coordinate type {ctype}')
#         if ctype.__name__ not in self.transforms:
#             available_transforms = ', '.join(self.transforms.keys())
#             message = 'Chained transformations/tree traversal is not implemented.' \
#                 + f'Available coordinate transformations are to {available_transforms}'
#             raise NotImplementedError(message)
#         return self.transforms[ctype.__name__](self)