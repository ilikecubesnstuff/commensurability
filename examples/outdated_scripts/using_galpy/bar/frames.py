from tqdm import tqdm
from itertools import count

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool


# square image, size of one side in pixels
SIZE = 100
# bar mass, in solar masses
OMEGA_MIN = 0e9  # solMass
OMEGA_MAX = 1e9  # solMass
FRAMES = 11

# range of R (cylindrical coordinates), in kiloparsecs
R_MIN = 0  # kpc
R_MAX = 8  # kpc
# range of tangential velocity, in kilometers per second
VT_MIN = 0  # km/s
VT_MAX = 400  # km/s
# integration parameters, in gigayears
STEPSIZE = 0.001  # Gyr
STEPS = 1000

# name
NAME = 'MW_BAR_STILL'
# save location
FILENAME = f'{NAME}_over_OMEGA_{OMEGA_MIN}-{OMEGA_MAX}__R_{R_MIN}-{R_MAX}__VT_{VT_MIN}-{VT_MAX}__INT_{STEPSIZE}_{STEPS}.npy'

# multiprocessing chunking size
CHUNKSIZE = 100

# ----------------------------------------------------

# helpful variables
X_RES = Y_RES = SIZE
SHAPE = (FRAMES, X_RES, Y_RES)
X_RANGE = (R_MIN, R_MAX)
Y_RANGE = (VT_MIN, VT_MAX)
EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)


# data arrays
# exclude the first point in X and Y, to avoid 0
OMEGA_ARR = np.linspace(OMEGA_MIN, OMEGA_MAX, FRAMES)  * u.solMass
T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr
X_ARR = np.linspace(R_MIN, R_MAX, X_RES + 1)[1:]  * u.kpc
Y_ARR = np.linspace(VT_MIN, VT_MAX, Y_RES + 1)[1:]  * u.km/u.s

# potentials
omega_rot = 0 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
rotpot_factory = lambda omega: [
    halo,
    disc,
    potential.SoftenedNeedleBarPotential(amp=omega, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega_rot),
    potential.NonInertialFrameForce(Omega=omega_rot)
]
potentials = [rotpot_factory(omega) for omega in OMEGA_ARR]
def compute_pixel(arg):
    frame, pot, i, r, j, v = arg
    initial_condition = [
        r, 
        0 * u.km / u.s, 
        v, 
        0 * u.kpc, 
        0 * u.km / u.s, 
        0 * u.deg
    ]
    o = orbit.Orbit(initial_condition)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    return frame, i, j, tess.area


def main():
    cube = np.zeros(SHAPE)
    pixels = [(frame, pot, i, x, j, y) for frame, pot in enumerate(potentials) for i, x in enumerate(X_ARR) for j, y in enumerate(Y_ARR)]
    with Pool() as p:
        image_data = [(frame, i, j, value) for frame, i, j, value in tqdm(p.imap_unordered(compute_pixel, pixels, CHUNKSIZE), total=cube.size)]

    # construct image
    for frame, i, j, value in image_data:
        cube[frame, i, j] = value

    np.save(FILENAME, cube)

    fig, ax = plt.subplots(figsize = (10, 10))
    ax.imshow(cube[0].T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
    plt.show()

if __name__ == '__main__':
    main()