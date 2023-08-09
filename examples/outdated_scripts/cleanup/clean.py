from tqdm import tqdm
from math import prod
from itertools import islice

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation
from commensurability.analysis import Analysis

from multiprocessing import Pool

import h5py


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]


SIZE = 10
coords = dict(
    R   = np.linspace(0, 10, SIZE + 1)[1:]  * u.kpc,
    vR  = np.linspace(0, 0, 1)  * u.km/u.s,
    vT  = np.linspace(0, 300, SIZE + 1)[1:]  * u.km/u.s,
    z   = np.linspace(1, 1, 1)  * u.kpc,
    vz  = np.linspace(0, 0, 1)  * u.km/u.s,
    phi = np.linspace(0, 0, 1)  * u.deg,
)
ts = np.linspace(0, 1, 501) * u.Gyr
canal = Analysis(pot, ts, pattern_speed=omega, **coords)
canal.construct_image()
canal.save_image('test.hdf5')
canal.display_image()