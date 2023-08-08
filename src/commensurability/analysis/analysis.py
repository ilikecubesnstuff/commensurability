from math import prod
from tqdm import tqdm

import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt

from ..tessellation import Tessellation
from ..utils import clump, make_quantity

import h5py


DIMENSIONLESS = u.s/u.s
KPC = u.kpc
KMS = u.km / u.s
DEG = u.deg


CYLINDRICAL_DEFAULTS = dict(
    R = KPC,
    vR = KMS,
    vT = KMS,
    z = KPC,
    vz = KMS,
    phi = DEG
)
OMEGA_DEFAULT = KMS/KPC


class Analysis:

    def __init__(self, pot, ts, *, pattern_speed=0, backend='galpy', **coords):
        self.pot = pot
        self.pattern_speed = pattern_speed
        self.phi_offset = (pattern_speed * ts).to(DIMENSIONLESS)

        
        # for now, only parse input in cylindrical coordinates
        if not all(key in coords for key in CYLINDRICAL_DEFAULTS):
            raise ValueError('Requires all cylindrical components specificied as keyword arguments.')
        self.variables = []
        for key, value in coords.items():
            coords[key] = quantity = make_quantity(value)
            if quantity.size != 1:
                self.variables.append(key)
        
        self.coords = coords

        if backend == 'galpy':
            import galpy
            self.backend = galpy
            self.evaluator = self.eval_with_galpy_backend
            self.ts = ts


    def eval_with_galpy_backend(self, *indices):
        N = len(indices[0])
        iter_inds = iter(indices)
        initial_conditions = [
            self.coords[key][next(iter_inds)]
                if key in self.variables
                else self.coords[key]*np.ones(N)
            for key in CYLINDRICAL_DEFAULTS
        ]

        orbits = self.backend.orbit.Orbit(initial_conditions)
        orbits.integrate(self.ts, self.pot)
        orbits.turn_physical_on()
        for orbit in orbits:
            R = orbit.R(self.ts)
            phi = orbit.phi(self.ts) + self.phi_offset

            x = R * np.cos(phi.value)
            y = R * np.sin(phi.value)
            z = orbit.z(self.ts)

            points = np.array([x, y, z]).T
            tess = Tessellation(points)
            yield tess.volume


    def construct_image(self, chunksize=200, progressbar=True):
        self.shape = tuple(coord.size for coord in self.coords.values() if coord.size != 1)
        self.image = np.zeros(self.shape)

        indices = np.ndindex(self.shape)
        chunked_indices = clump(indices, size=chunksize)
        for chunk in tqdm(chunked_indices, size=prod(self.shape)//chunksize, disable=~progressbar):
            chunk = np.array(chunk)
            values = self.evaluator(*chunk.T)
            for i, value in zip(chunk, values):
                self.image[tuple(i)] = value
    
    def save_image(self, filename):
        with h5py.File(filename, 'w-') as f:
            dset = f.create_dataset('image', data=self.image)
            dset.attrs['R_min'] = np.min(self.coords['R'])
            dset.attrs['R_max'] = np.max(self.coords['R'])
            dset.attrs['vR_min'] = np.min(self.coords['vR'])
            dset.attrs['vR_max'] = np.max(self.coords['vR'])
            dset.attrs['vT_min'] = np.min(self.coords['vT'])
            dset.attrs['vT_max'] = np.max(self.coords['vT'])
            dset.attrs['z_min'] = np.min(self.coords['z'])
            dset.attrs['z_max'] = np.max(self.coords['z'])
            dset.attrs['vz_min'] = np.min(self.coords['vz'])
            dset.attrs['vz_max'] = np.max(self.coords['vz'])
            dset.attrs['phi_min'] = np.min(self.coords['phi'])
            dset.attrs['phi_max'] = np.max(self.coords['phi'])

    def display_image(self):
        plt.imshow(self.image, origin='lower')
        plt.show()

