from __future__ import annotations
from typing import MutableMapping
from collections.abc import Collection

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
                # print('TRANSFORM FUNCTION', obj.__annotations__)
                namespace[attr] = obj
                transforms[obj.__annotations__['return']] = obj
        namespace.pop('Transforms', None)
        # print('TRANSFORMS', transforms_class.__dict__)

        init_params = ', '.join(f'{axis}: {dtype.__name__}' for axis in axes)
        init_body = '\n'.join(
f'''
    {axis} = make_collection({axis})
    {axis} = make_quantity({axis}, unit={unit})
    self.{axis} = {axis}
'''
for axis, unit in axes.items()
        )
        body = (
f'''
def __init__(self, {init_params}):
    {init_body}
    self.shape = tuple(getattr(self, axis).size for axis in self.axes)

def __repr__(self):
    return f"{name}Coordinates(" + ", ".join(f"{{axis}}={{getattr(self, axis)}}" for axis in self.axes) + ")"
'''
        )
        exec(body, globals(), namespace)

        # print('NEW CLASS', name, bases, namespace)
        return super().__new__(metacls, name, bases, namespace)


coordinate_registry = {}
class CoordinateType(metaclass=CoordinateMeta):

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        coordinate_registry[cls.__name__] = cls

    def to(self, ctype: CoordinateType) -> CoordinateType:
        if ctype.__name__ not in coordinate_registry:
            raise TypeError(f'Unrecognized coordinate type {ctype}')
        if ctype.__name__ not in self.transforms:
            available_transforms = ', '.join(self.transforms.keys())
            message = f'Chained transformations/tree traversal is not implemented. Available coordinate transformations are to {available_transforms}'
            raise NotImplemented(message)
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


class Spherical(CoordinateType):
    R: u.kpc
    phi: u.deg
    theta: u.deg
    vR: u.km / u.s
    v_alt: u.km / u.s
    v_az: u.km / u.s

    class Transforms:
        def to_cartesian(self) -> Cartesian:
            pass



