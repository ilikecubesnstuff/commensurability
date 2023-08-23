import typing
from typing import (
    Iterable
)

import numpy as np
import astropy.units as u

from ...utils import make_quantity
from ..coordinates import Coordinate, Cylindrical
from .base import Backend


class GalpyBackend(Backend):

    def __imports__():
        import galpy.orbit

    @staticmethod
    def format_coordinate(coord: Coordinate):
        # assume coord is of len/size 1
        # print(coord)
        if isinstance(coord, Cylindrical):
            return [
                coord.R,
                coord.vR,
                coord.vT,
                coord.z,
                coord.vz,
                coord.phi
            ]
        raise NotImplementedError('Only cylindrical coordinates accepted for galpy backend')

    def _extract_points_from_orbit(self,
                                   orbit: typing.Any,
                                   *,
                                   t: u.Quantity,
                                   phi_offset: u.Quantity
                                   ):
        R = orbit.R(t)
        phi = orbit.phi(t) + phi_offset.to(u.dimensionless_unscaled)

        x = R * np.cos(phi.value)
        y = R * np.sin(phi.value)
        z = orbit.z(t)

        return np.array([x, y, z]).T

    def _compute_orbit(self, coord: Coordinate, *, t: u.Quantity, pot: typing.Any, **kwargs):
        initial_condition = self.format_coordinate(coord)
        orbit = self.galpy.orbit.Orbit(initial_condition)
        orbit.integrate(t, pot, **kwargs)
        return orbit

    def _compute_orbits(self,
                        coords: Iterable[Coordinate],
                        *,
                        t: u.Quantity,
                        pot: typing.Any,
                        **kwargs
                        ):
        initial_conditions = tuple(map(self.format_coordinate, coords))
        orbits = self.galpy.orbit.Orbit(initial_conditions)
        orbits.integrate(t, pot, **kwargs)
        return orbits

    def _precompute_namespace_hook(self, namespace: typing.MutableMapping):
        pot = namespace['pot']
        dt = make_quantity(namespace['dt'], u.Gyr)
        steps = namespace['steps']
        omega = make_quantity(namespace['pattern_speed'], u.km / u.s / u.kpc)

        if isinstance(steps, typing.Collection):
            steps = steps[-1]
        t = np.arange(steps) * dt
        phi_offset = t * omega

        computing_kwargs = dict(t=t, pot=pot, progressbar=False)
        extracting_kwargs = dict(t=t, phi_offset=phi_offset)
        return computing_kwargs, extracting_kwargs
