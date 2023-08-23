from __future__ import annotations
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

from abc import abstractstaticmethod
from tqdm import tqdm

import numpy as np
import astropy.units as u

from ..utils import clump, make_quantity, get_top_level_package
from .backend import GalpyBackend, GalaBackend, AgamaBackend
from .backend.base import Backend
from .coordinates import Coordinate


class Analysis:

    def __init__(self,
                 potential_function: Callable[[], Any],
                 step_size__dt: Union[float, u.Quantity],
                 step_total__n: int,
                 *,
                 pattern_speed: Union[float, u.Quantity] = 0.0,
                 backend: Optional[Union[str, Backend]] = None,
                 ) -> None:

        self._potential_function = potential_function
        self.potential = potential_function()

        self.dt = make_quantity(step_size__dt, unit=u.Gyr)
        self.n = step_total__n

        self.pattern_speed = make_quantity(pattern_speed, unit=u.km / u.s / u.kpc)

        if backend is None: backend = get_top_level_package(self.potential)
        if backend == 'galpy': backend = GalpyBackend()
        if backend == 'gala': backend = GalaBackend()
        if backend == 'agama': backend = AgamaBackend()
        if not isinstance(backend, Backend):
            raise TypeError(f'Unrecognized backend {backend}')
        self.backend = backend

    @abstractstaticmethod
    def __eval__(self, points: np.ndarray) -> float:
        pass

    def construct_image(self,
                        coords: Coordinate,
                        chunksize: int = 200,
                        progressbar: bool = True,
                        ) -> np.ndarray:
        self.coords = coords
        varaxes = tuple(s > 1 for s in coords.shape)
        self.axes = tuple(axis for isvar, axis in zip(varaxes, coords.axes) if isvar)
        self.shape = tuple(s for isvar, s in zip(varaxes, coords.shape) if isvar)
        self.image = np.zeros(len(self.coords))

        coords = clump(coords, chunksize)
        i = 0
        for coords_chunk in tqdm(coords, desc=f'with {chunksize=}', disable=not progressbar):
            orb_it = self.backend.iter_orbits(
                pot = self.potential,
                coords=coords_chunk,
                dt=self.dt,
                steps=self.n,
                pattern_speed=self.pattern_speed
            )
            for points in orb_it:
                value = self.__eval__(points)
                self.image[i] = value
                i += 1
        
        self.image = self.image.reshape(self.shape)
        return self.image


from ..tessellation import Tessellation

class TessellationAnalysis(Analysis):

    @staticmethod
    def __eval__(points):
        tess = Tessellation(points)
        return tess.calculate_measure()
