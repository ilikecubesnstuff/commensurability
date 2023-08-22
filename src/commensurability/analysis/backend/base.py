from __future__ import annotations

from abc import abstractmethod, abstractstaticmethod
from itertools import pairwise, islice
import typing

import numpy as np
import astropy.units as u

from ..importextension import ExtendImports
from ..coordinates import Coordinate, CoordinateCollection


class Backend(ExtendImports):

    def __imports__():
        # when subclassing, include extra imports here
        # these get added to the object's namespace
        # use them via attribute access
        ...

    @abstractstaticmethod
    def _extract_points_from_orbit(orbit: typing.Any,
                                   **kwargs
                                   ) -> np.ndarray:
        pass

    @abstractmethod
    def _compute_orbit(self, 
                       coord: Coordinate,
                       **kwargs):
        pass

    @abstractmethod
    def _compute_orbits(self,
                        coords: CoordinateCollection,
                        **kwargs):
        pass

    def _precompute_namespace_hook(self,
                                   namespace: typing.MutableMappin
                                   ) -> tuple[dict, dict]:
        return {}, {}

    def get_orbit(self,
                  pot: typing.Any,
                  coord: Coordinate,
                  dt: typing.Union[float, typing.Collection],
                  steps: int,
                  *,
                  pattern_speed: u.Quantity = 0,
                  **kwargs
                  ) -> np.ndarray:
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbit = self._compute_orbit(coord, **computing_kwargs, **kwargs)
        return self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbits(self,
                    pot: typing.Any,
                    coords: CoordinateCollection,
                    dt: typing.Union[float, typing.Collection],
                    steps: int,
                    *,
                    pattern_speed: u.Quantity = 0,
                    **kwargs
                    ) -> typing.Iterator[np.ndarray]:
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            yield self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbit_slices(self,
                          pot: typing.Any,
                          coords: CoordinateCollection,
                          dt: typing.Union[float, typing.Collection],
                          *steps: int,
                          pattern_speed: u.Quantity = 0,
                          **kwargs
                          ) -> typing.Iterator[tuple[np.ndarray]]:
        steps = [0] + sorted(steps)
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            points = self._extract_points_from_orbit(orbit, **extracting_kwargs)
            iter_points = iter(points)
            yield (np.array(list(islice(iter_points, s2-s1))) for s1, s2 in pairwise(steps))
