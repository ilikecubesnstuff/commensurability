from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Union, Sequence, Iterable, Collection, MutableMapping
from importlib import import_module
from itertools import pairwise, islice

import numpy as np
import astropy.units as u

from .coordinates import Coordinate, CoordinateCollection, Cylindrical
from ..utils import make_quantity, make_collection, make_sequence


DT_TYPE = Union[float, Collection]



class BackendMeta(ABCMeta):
    def unavailable(e):
        class Unavailable:
            def __init__(self):
                raise ModuleNotFoundError(e)
        return Unavailable

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
        packages = namespace.get('__require__', ())
        if not isinstance(packages, tuple):
            packages = (packages,)
        try:
            for package in packages:
                namespace[package] = import_module(package)
        except ModuleNotFoundError as e:
            return metacls.unavailable(e)
        return super().__new__(metacls, name, bases, namespace)


class Backend(metaclass=BackendMeta):
    pass


class GalpyBackend(Backend):
    __require__ = ('galpy', 'galpy.orbit')

    @staticmethod
    def format_coordinate(coordinate: Coordinate):
        if isinstance(coordinate, Cylindrical.Coordinate):
            return [
                coordinate.R,
                coordinate.vR,
                coordinate.vT,
                coordinate.z,
                coordinate.vz,
                coordinate.phi
            ]
        raise NotImplementedError('Only cylindrical coordinates accepted for galpy backend')

    def iter_compute_orbits(self, pot, coordinates: CoordinateCollection, dt: DT_TYPE, steps: int, *, pattern_speed: u.Quantity = 0):
        dt = make_quantity(dt, u.Gyr)
        pattern_speed = make_quantity(pattern_speed, u.km / u.s / u.kpc)

        initial_conditions = tuple(map(self.format_coordinate, coordinates))
        ts = np.arange(steps) * make_quantity(dt)
        phi_offset = (ts * pattern_speed).to(u.dimensionless_unscaled)

        def extract_points(orbit):
            R = orbit.R(ts)
            phi = orbit.phi(ts) + phi_offset

            x = R * np.cos(phi.value)
            y = R * np.sin(phi.value)
            z = orbit.z(ts)

            return np.array([x, y, z]).T

        orbits = self.galpy.orbit.Orbit(initial_conditions)
        orbits.integrate(ts, pot)
        yield from map(extract_points, orbits)
    
    def iter_compute_orbit_slices(self, pot, coordinates: CoordinateCollection, dt: DT_TYPE, *steps: int, pattern_speed: u.Quantity = 0):
        dt = make_quantity(dt, u.Gyr)
        pattern_speed = make_quantity(pattern_speed, u.km / u.s / u.kpc)
        steps = [0] + sorted(steps)

        initial_conditions = tuple(map(self.format_coordinate, coordinates))
        ts = np.arange(steps[-1]) * make_quantity(dt)
        phi_offset = (ts * pattern_speed).to(u.dimensionless_unscaled)

        def extract_points(orbit):
            R = orbit.R(ts)
            phi = orbit.phi(ts) + phi_offset

            x = R * np.cos(phi.value)
            y = R * np.sin(phi.value)
            z = orbit.z(ts)

            iter_points = iter(np.array([x, y, z]).T)
            yield from (np.array(list(islice(iter_points, s2-s1))) for s1, s2 in pairwise(steps))

        orbits = self.galpy.orbit.Orbit(initial_conditions)
        orbits.integrate(ts, pot)
        yield from map(extract_points, orbits)


class GalaBackend(Backend):
    __require__ = 'gala'


class AgamaBackend(Backend):
    __require__ = 'agama'