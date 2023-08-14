from abc import abstractmethod
from math import prod
from tqdm import tqdm
from pathlib import Path

import h5py
import numpy as np

from ..tessellation import Tessellation
from ..utils import clump, get_top_level_package
from .backends import Backend
from .backends import GalpyBackend
from .backends import GalaBackend
from .backends import AgamaBackend
from .interactive import InteractivePhasePlot


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

    def evaluate(self, points):
        tess = Tessellation(points)
        return tess.calculate_measure()

    def construct_image(self, coords, chunksize=200, progressbar=True):
        self.coords = coords
        varaxes = tuple(s > 1 for s in coords.shape)
        self.axes = tuple(axis for isvar, axis in zip(varaxes, coords.axes) if isvar)
        self.shape = tuple(s for isvar, s in zip(varaxes, coords.shape) if isvar)
        self.image = np.zeros(prod(self.shape))

        coords = clump(coords, chunksize)
        i = 0
        for coords_chunk in tqdm(coords):
            orb_it = self.backend.iter_orbits(self.pot, coords_chunk, self.dt, self.steps, pattern_speed=self.pattern_speed)
            for points in orb_it:
                value = self.evaluate(points)
                self.image[i] = value
                i += 1
        
        self.image = self.image.reshape(self.shape)
    
    def save_image(self, filename):
        with h5py.File(filename, 'w-') as f:
            dset = f.create_dataset('image', data=self.image)
            dset.attrs['R'] = self.coords['R']
            dset.attrs['vR'] = self.coords['vR']
            dset.attrs['vT'] = self.coords['vT']
            dset.attrs['z'] = self.coords['z']
            dset.attrs['vz'] = self.coords['vz']
            dset.attrs['phi'] = self.coords['phi']
            dset.attrs['omega'] = self.pattern_speed
            dset.attrs['times'] = self.ts
    
    def launch_interactive_plot(self):
        plot = InteractivePhasePlot(self)
        plot.show()


class TessEval:

    def evaluate(self, points):
        tess = Tessellation(points)
        return tess.calculate_measure()
