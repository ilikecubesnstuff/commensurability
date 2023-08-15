from abc import abstractstaticmethod
from math import prod
from tqdm import tqdm

import h5py
import numpy as np

from ..tessellation import Tessellation
from ..utils import clump, get_top_level_package
from .coordinates import Cylindrical
from . import backends
from .backends import Backend
from .backends import GalpyBackend
from .backends import GalaBackend
from .backends import AgamaBackend
from .interactive import InteractivePhasePlot
from .fileio import FileIO

class Analysis:

    def __init__(self, pot, dt, steps, *, pattern_speed=0, backend=None):
        self.pot = pot
        self.dt = dt
        self.steps = steps
        self.pattern_speed = pattern_speed

        if backend is None:
            backend = get_top_level_package(pot)
        if not isinstance(backend, Backend):
            if backend == 'galpy':
                self.backend = GalpyBackend()
            if backend == 'gala':
                self.backend = GalaBackend()
            if backend == 'agama':
                self.backend = AgamaBackend()
        else:
            self.backend = backend
    
    def __save__(self):
        _, attrs = self.coords.__save__()
        if not hasattr(self, 'pot_string'):
            raise AttributeError(f'Please set {self.__class__.__name__}.pot_string to a '
                                 f'string of the code used to generate the potential.')
        attrs['dt'] = self.dt
        attrs['pattern_speed'] = self.pattern_speed
        attrs['steps'] = self.steps
        attrs['pot_code'] = np.void(self.pot_string.encode('utf8'))
        attrs['backend'] = np.void(self.backend.__class__.__name__.encode('utf8'))
        return self.image, attrs

    @classmethod
    def __read__(cls, file):
        namespace = {}
        exec(file.attrs['pot_code'].tobytes().decode('utf8'), {}, namespace)

        pot = namespace['pot']
        dt = file.attrs['dt']
        steps = file.attrs['steps']
        pattern_speed = file.attrs['pattern_speed']
        backend = getattr(backends, file.attrs['backend'].tobytes().decode('utf8'))()
        obj = cls(pot, dt, steps, pattern_speed=pattern_speed, backend=backend)
        coords = Cylindrical.__read__(file)
        obj.read_proxy(coords)
        obj.image = file[()]
        return obj

    def read_proxy(self, coords):
        self.coords = coords
        varaxes = tuple(s > 1 for s in coords.shape)
        self.axes = tuple(axis for isvar, axis in zip(varaxes, coords.axes) if isvar)
        self.shape = tuple(s for isvar, s in zip(varaxes, coords.shape) if isvar)
        self.image = np.zeros(prod(self.shape))

    @abstractstaticmethod
    def __eval__(self, points):
        pass

    def construct_image(self, coords, chunksize=200, progressbar=True):
        self.coords = coords
        varaxes = tuple(s > 1 for s in coords.shape)
        self.axes = tuple(axis for isvar, axis in zip(varaxes, coords.axes) if isvar)
        self.shape = tuple(s for isvar, s in zip(varaxes, coords.shape) if isvar)
        self.image = np.zeros(prod(self.shape))

        coords = clump(coords, chunksize)
        i = 0
        for coords_chunk in tqdm(coords):
            orb_it = self.backend.iter_orbits(
                pot=self.pot,
                coords=coords_chunk,
                dt=self.dt,
                steps=self.steps,
                pattern_speed=self.pattern_speed,
                numcores=8
            )
            for points in orb_it:
                value = self.__eval__(points)
                self.image[i] = value
                i += 1

        self.image = self.image.reshape(self.shape)

    def save_image(self, filename):
        file = FileIO(filename)
        file.save(self)
        return file

    def launch_interactive_plot(self):
        plot = InteractivePhasePlot(self)
        plot.show()


class TessellationAnalysis(Analysis):

    @staticmethod
    def __eval__(points):
        tess = Tessellation(points)
        return tess.calculate_measure()
