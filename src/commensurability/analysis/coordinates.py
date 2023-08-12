from __future__ import annotations
from collections.abc import Collection
from typing import MutableMapping

import numpy as np
import astropy.units as u


def make_quantity(obj, unit=u.dimensionless_unscaled):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit


def make_collection(obj, cls=list):
    if not issubclass(cls, Collection):
        raise ValueError('Class provided must subclass collections.abc.Collection')

    if not isinstance(obj, Collection):
        obj = cls([obj])
    return obj


class CoordinateMeta(type):

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping, dtype=float):
        axes = namespace.get('__annotations__', {})
        namespace['axes'] = tuple(axes.keys())

        transforms_class = namespace.get('Transforms', type('Transforms', (), {}))
        namespace['transforms'] = transforms = {}
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
            f'\n'
            f'def __repr__(self):\n'
            f'    return f\'{name}Coordinates({repr_body})\'\n'
        )
        exec(body, globals(), namespace)
        return super().__new__(metacls, name, bases, namespace)


class CoordinateType(metaclass=CoordinateMeta):
    registry = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        CoordinateType.registry[cls.__name__] = cls

    def to(self, ctype: CoordinateType) -> CoordinateType:
        if ctype.__name__ not in CoordinateType.registry:
            raise TypeError(f'Unrecognized coordinate type {ctype}')
        if ctype.__name__ not in self.transforms:
            available_transforms = ', '.join(self.transforms.keys())
            message = 'Chained transformations/tree traversal is not implemented.' \
                + f'Available coordinate transformations are to {available_transforms}'
            raise NotImplementedError(message)
        return self.transforms[ctype.__name__](self)


class Cartesian(CoordinateType):
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


class Cylindrical(CoordinateType):
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


class Spherical(CoordinateType):
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
