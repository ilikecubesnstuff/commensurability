from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from typing import Any, Union, Collection, MutableMapping
from importlib import import_module
from itertools import pairwise, islice

import numpy as np
import astropy.units as u

from .importextension import ExtendImports
from .coordinates import Coordinate, CoordinateCollection, Cylindrical
from ..utils import make_quantity


class Backend(ExtendImports):

    def __imports__():
        # when subclassing, include extra imports here
        # these get added to the object's namespace
        # use them via attribute access
        ...

    @abstractstaticmethod
    def _extract_points_from_orbit(self, orbit: Any, **kwargs):
        pass

    @abstractmethod
    def _compute_orbit(self, coord: Coordinate, **kwargs):
        pass

    @abstractmethod
    def _compute_orbits(self, coords: CoordinateCollection, **kwargs):
        pass

    def _precompute_namespace_hook(self, namespace: MutableMapping):
        return {}, {}

    def get_orbit(self, pot: Any, coord: Coordinate,
                  dt: Union[float, Collection], steps: int, *, pattern_speed: u.Quantity = 0, **kwargs):
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbit = self._compute_orbit(coord, **computing_kwargs, **kwargs)
        return self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbits(self, pot: Any, coords: CoordinateCollection,
                    dt: Union[float, Collection], steps: int, *, pattern_speed: u.Quantity = 0, **kwargs):
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            yield self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbit_slices(self, pot: Any, coords: CoordinateCollection,
                          dt: Union[float, Collection], *steps: int, pattern_speed: u.Quantity = 0, **kwargs):
        steps = [0] + sorted(steps)
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            points = self._extract_points_from_orbit(orbit, **extracting_kwargs)
            iter_points = iter(points)
            yield (np.array(list(islice(iter_points, s2-s1))) for s1, s2 in pairwise(steps))


class GalpyBackend(Backend):

    def __imports__():
        import galpy
        import galpy.orbit

    @staticmethod
    def format_coordinate(coord: Coordinate):
        print(coord)
        if isinstance(coord, Cylindrical.Coordinate):
            return [
                coord.R,
                coord.vR,
                coord.vT,
                coord.z,
                coord.vz,
                coord.phi
            ]
        raise NotImplementedError('Only cylindrical coordinates accepted for galpy backend')

    def _extract_points_from_orbit(self, orbit: Any, *, t: u.Quantity, phi_offset: u.Quantity):
        R = orbit.R(t)
        phi = orbit.phi(t) + phi_offset

        x = R * np.cos(phi.value)
        y = R * np.sin(phi.value)
        z = orbit.z(t)

        return np.array([x, y, z]).T

    def _compute_orbit(self, coord: Coordinate, *, t: u.Quantity, pot: Any, **kwargs):
        initial_condition = self.format_coordinate(coord)
        orbit = self.galpy.orbit.Orbit(initial_condition)
        orbit.integrate(t, pot, **kwargs)
        return orbit

    def _compute_orbits(self, coords: CoordinateCollection, *, t: u.Quantity, pot: Any, **kwargs):
        initial_conditions = tuple(map(self.format_coordinate, coords))
        orbits = self.galpy.orbit.Orbit(initial_conditions)
        orbits.integrate(t, pot, **kwargs)
        return orbits

    def _precompute_namespace_hook(self, namespace: MutableMapping):
        pot = namespace['pot']
        dt = make_quantity(namespace['dt'], u.Gyr)
        steps = namespace['steps']
        omega = make_quantity(namespace['pattern_speed'], u.km / u.s / u.kpc)

        if isinstance(steps, Collection):
            steps = steps[-1]
        t = np.arange(steps) * dt
        phi_offset = (t * omega).to(u.dimensionless_unscaled)

        computing_kwargs = dict(t=t, pot=pot, progressbar=False)
        extracting_kwargs = dict(t=t, phi_offset=phi_offset)
        return computing_kwargs, extracting_kwargs


class GalaBackend(Backend):

    def __imports__():
        import gala


class AgamaBackend(Backend):

    def __imports__():
        import agama
