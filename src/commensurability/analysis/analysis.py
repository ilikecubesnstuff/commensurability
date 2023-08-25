from __future__ import annotations
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)

from abc import abstractstaticmethod
import inspect
from tqdm import tqdm

import numpy as np
import astropy.units as u

from ..utils import clump, make_quantity, get_top_level_package
from .backend import GalpyBackend, GalaBackend, AgamaBackend
from .backend.base import Backend
from .coordinates import Coordinate

# move to "persistence" subpackage later
from .fileio import FileIO
from .coordinates import Cylindrical
from . import backend
from .interactive import InteractivePhasePlot

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

    # persistence methods

    def __save__(self):
        potsource = inspect.getsource(self._potential_function)
        potsource.replace(self._potential_function.__name__, 'potential_function', 1)
        attrs = dict(
            R = self.coords.R,
            vR = self.coords.vR,
            vT = self.coords.vT,
            z = self.coords.z,
            vz = self.coords.vz,
            phi = self.coords.phi,
            dt = self.dt,
            steps = self.n,
            pattern_speed = self.pattern_speed,
            backend = np.void(self.backend.__class__.__name__.encode('utf8')),
            potfunc = np.void(potsource.encode('utf8')),
        )
        print(self.image)
        return attrs, self.image

    @classmethod
    def __read__(cls, dset):
        if 'potfunc' in dset.attrs:
            potsource = dset.attrs['potfunc'].tobytes().decode('utf8')
            namespace = {}
            exec(potsource, {'u': u}, namespace)
            potfunc = namespace['potential_function']
        else:
            print('Warning! No potential function defined.')
            potfunc = lambda: None

        backend_cls = getattr(backend, dset.attrs['backend'].tobytes().decode('utf8'))
        analysis = cls(
            potfunc,
            dset.attrs['dt'],
            dset.attrs['steps'],
            pattern_speed=dset.attrs['pattern_speed'],
            backend=backend_cls()
        )

        coords = Cylindrical(
            R=dset.attrs['R'],
            vR=dset.attrs['vR'],
            vT=dset.attrs['vT'],
            z=dset.attrs['z'],
            vz=dset.attrs['vz'],
            phi=dset.attrs['phi'],
        )
        analysis.coords = coords
        varaxes = tuple(s > 1 for s in coords.shape)
        analysis.axes = tuple(axis for isvar, axis in zip(varaxes, coords.axes) if isvar)
        analysis.shape = tuple(s for isvar, s in zip(varaxes, coords.shape) if isvar)

        analysis.image = dset[()]
        return analysis

    def save_image(self, filename):
        file = FileIO(filename)
        file.save(self)
        return file

    def launch_interactive_plot(self):
        plot = InteractivePhasePlot(self)
        plot.show()


from ..tessellation import Tessellation

class TessellationAnalysis(Analysis):

    @staticmethod
    def __eval__(points):
        tess = Tessellation(points)
        return tess.calculate_measure()
