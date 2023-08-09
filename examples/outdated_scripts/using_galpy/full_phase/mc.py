import os
from tqdm import tqdm
from pathlib import Path
from itertools import count

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool


# SETUP VALUES --------------------------------

# R in kiloparsecs
R_MAX = 10   # kpc
R_RES = 100
# vR in kilometers/second
VR_MAX = 200  # km/s
VR_RES = 200
# vT in kilometers/second
VT_MAX = 600  # km/s
VT_RES = 300
# z in kiloparsecs
Z_MAX = 6    # kpc
Z_RES = 60
# vs in kilometers/second
VZ_MAX = 300  # km/s
VZ_RES = 300
# phi in degrees
PHI_MAX = 90  # deg
PHI_RES = 10
# integration time in gigayears
T_MAX = 2
T_RES = 400

# saving frequency in orbits
SAVE_FREQ = 100

# END OF SETUP VALUES --------------------------

# creating MW-like potential
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
rotpot_factory = lambda omega: [
    halo,
    disc,
    potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
    potential.NonInertialFrameForce(Omega = omega)
]
omega = 30  * u.km/u.s/u.kpc
POTENTIAL = rotpot_factory(omega=omega)

# random initial condition
def random_ic():
    return [
        np.random.uniform(0, 20),
        np.random.uniform(0, 600),
        np.random.uniform(0, 600),
        np.random.uniform(0, 6),
        np.random.uniform(0, 0),
        np.random.uniform(0, 180),
    ]

# creating value arrays
arr_factory = lambda max, res: np.linspace(0, max, res + 1)[1:]
R_ARR   = arr_factory(  R_MAX,   R_RES)
# VR_ARR  = arr_factory( VR_MAX,  VR_RES)
VT_ARR  = arr_factory( VT_MAX,  VT_RES)
Z_ARR   = arr_factory(  Z_MAX,   Z_RES)
# VZ_ARR  = arr_factory( VZ_MAX,  VZ_RES)
PHI_ARR = np.linspace(0, 90, 10)

VR_RES = 1; VR_ARR = np.array([0])
VZ_RES = 1; VZ_ARR = np.array([0])
Ri, VRi, VTi, Zi, VZi, PHIi = np.meshgrid(R_ARR, VR_ARR, VT_ARR, Z_ARR, VZ_ARR, PHI_ARR, indexing='ij')

# setting up path for saving
path = Path('.') / '6d_thingy.npy'
if not path.is_file():
    shape = (R_RES, VR_RES, VT_RES, Z_RES, VZ_RES, PHI_RES)
    data = np.ones(shape)
    nearest = np.ones(shape) * np.inf

    with path.open(mode='wb') as f:
        np.save(f, data)
        np.save(f, nearest)

with path.open(mode='rb') as f:
    data = np.load(f)
    nearest = np.load(f)
print(data.shape, nearest.shape)


DR = R_MAX/R_RES
DVR = VR_MAX/VR_RES
DVT = VT_MAX/VT_RES
DZ = Z_MAX/Z_RES
DVZ = VZ_MAX/VZ_RES
DPHI = PHI_MAX/PHI_RES
T_ARR = np.linspace(0, T_MAX, T_RES + 1)
try:
    for it in tqdm(count()):
        R, vR, vT, z, vz, phi = random_ic()
        ic = [
            R   * u.kpc,
            vR  * u.km/u.s,
            vT  * u.km/u.s,
            z   * u.kpc,
            vz  * u.km/u.s,
            phi * u.deg,
        ]
        o = orbit.Orbit(ic)
        o.integrate(T_ARR, POTENTIAL, method='dopr54_c')

        tess = Tessellation.from_galpy_orbit(o)
        value = tess.volume

        for R, vR, vT, z, vz, phi in o.getOrbit():
            dist = sum((
                abs(R/DR - Ri),
                abs(vR/DVR - VRi),
                abs(vT/DVT - VTi),
                abs(z/DZ - Zi),
                abs(vz/DVZ - VZi),
                abs(phi/DPHI - PHIi)
            ))
            mask = (dist < nearest)
            if not np.sum(mask):
                continue
            
            data[mask] = value
            nearest[mask] = dist[mask]

        if it%SAVE_FREQ == 0:
            with path.open('wb') as f:
                np.save(f, data)
                np.save(f, nearest)
finally:
    with path.open('wb') as f:
        np.save(f, data)
        np.save(f, nearest)
