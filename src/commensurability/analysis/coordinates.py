from __future__ import annotations
from collections.abc import Collection, Sequence
from dataclasses import make_dataclass
from math import prod
from typing import Mapping, MutableMapping

import numpy as np
import astropy.units as u

from ..utils import make_collection, make_quantity


class CoordinateCollectionMeta(type):

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping, dtype=float):
        axes = namespace.get('__annotations__', {})
        namespace['axes'] = tuple(axes.keys())

        transforms_class = namespace.get('Transforms', type('Transforms', (), {}))
        namespace['transforms'] = transforms = {
            name: (lambda self: self)
        }
        for attr, obj in vars(transforms_class).items():
            if callable(obj):
                namespace[attr] = obj
                transforms[obj.__annotations__['return']] = obj
        namespace.pop('Transforms', None)

        init_params = ', '.join(f'{axis}: {dtype.__name__}' for axis in axes)
        init_body = '\n'.join((
            f'    {axis} = make_collection({axis})\n'
            f'    {axis} = make_quantity({axis}, unit={unit})\n'
            f'    self.{axis} = {axis}\n'
        ) for axis, unit in axes.items())
        repr_body = f'{name}Coordinates({{", ".join(f"{{axis}}={{getattr(self, axis)}}" for axis in self.axes)}})'
        body = (
            f'def __init__(self, {init_params}):\n'
            f'{init_body}\n'
            f'    self.shape = tuple(getattr(self, axis).size for axis in self.axes)\n'
            f'    self.Coordinate = make_dataclass(f"{name}Coordinate", self.axes, bases=(Coordinate,))'
            f'\n'
            f'def __repr__(self):\n'
            f'    return f\'{repr_body}\'\n'
        )
        # print(body)
        exec(body, globals(), namespace)
        return super().__new__(metacls, name, bases, namespace)


class CoordinateCollection(metaclass=CoordinateCollectionMeta):
    class Coordinate:
        pass
    type_registry = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        CoordinateCollection.type_registry[cls.__name__] = cls
    
    def __contains__(self, item):
        if isinstance(item, Mapping):
            return all(item[axis] in getattr(self, axis) for axis in self.axes)
        if isinstance(item, Sequence):
            return all(item[i] in getattr(self, axis) for i, axis in enumerate(self.axes))
        raise NotImplementedError('Membership can only be tested on Mapping or Sequence types.')

    def __len__(self):
        return prod(self.shape)
    
    def __iter__(self):
        for indices in np.ndindex(self.shape):
            coords = {axis: getattr(self, axis)[i] for i, axis in zip(indices, self.axes)}
            yield self.Coordinate(**coords)

    def to(self, ctype: CoordinateCollection) -> CoordinateCollection:
        if ctype.__name__ not in CoordinateCollection.type_registry:
            raise TypeError(f'Unrecognized coordinate type {ctype}')
        if ctype.__name__ not in self.transforms:
            available_transforms = ', '.join(self.transforms.keys())
            message = 'Chained transformations/tree traversal is not implemented.' \
                + f'Available coordinate transformations are to {available_transforms}'
            raise NotImplementedError(message)
        return self.transforms[ctype.__name__](self)
Coordinate = CoordinateCollection.Coordinate


class Cartesian(CoordinateCollection):
    x: u.kpc
    y: u.kpc
    z: u.kpc
    vx: u.km / u.s
    vy: u.km / u.s
    vz: u.km / u.s

    class Transforms:
        def to_cylindrical(self) -> Cylindrical:
            R = np.sqrt(self.x ** 2 + self.y ** 2)
            phi = np.arctan2(self.y, self.x)
            vR = (self.x * self.vx + self.y * self.vy)/R
            vT = (-self.y * self.vx + self.x * self.vy)/R
            return Cylindrical(R=R, vR=vR, vT=vT, z=self.z, vz=self.vz, phi=phi)


class Cylindrical(CoordinateCollection):
    R: u.kpc
    vR: u.km / u.s
    vT: u.km / u.s
    z: u.kpc
    vz: u.km / u.s
    phi: u.deg

    class Transforms:
        def to_cartesian(self) -> Cartesian:
            x = self.R * np.cos(self.phi)
            y = self.R * np.sin(self.phi)

            vx = self.vR * np.cos(self.phi) - self.vT * np.sin(self.phi)
            vy = self.vT * np.cos(self.phi) + self.vR * np.sin(self.phi)

            return Cartesian(x=x, y=y, z=self.z, vx=vx, vy=vy, vz=self.vz)

        def to_cylindrical(self) -> Cylindrical:
            R = np.sqrt(self.R**2 + self.z**2)
            theta = np.arctan2(self.R, self.z)

            vR = (self.R * self.vR + self.z * self.vz)/R
            v_alt = (self.z * self.vR - self.R * self.vz)/R

            return Spherical(R=R, phi=self.phi, theta=theta, vR=vR, v_alt=v_alt, v_az=self.vT)


class Spherical(CoordinateCollection):
    R: u.kpc
    phi: u.deg
    theta: u.deg
    vR: u.km / u.s
    v_alt: u.km / u.s
    v_az: u.km / u.s

    class Transforms:
        def to_cylindrical(self) -> Cylindrical:
            R = self.R * np.sin(self.theta)
            z = self.R * np.cos(self.theta)

            vR = np.sin(self.theta) * self.vR + np.cos(self.theta) * self.v_alt
            vz = np.cos(self.theta) * self.vR - np.sin(self.theta) * self.v_alt

            return Cylindrical(R=R, phi=self.phi, z=z, vR=vR, vT=self.v_az, vz=vz)
