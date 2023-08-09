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

# range of R (cylindrical coordinates), in kiloparsecs
R_MIN = 0  # kpc
R_MAX = 8  # kpc
# range of tangential velocity, in kilometers per second
VT_MIN = 0  # km/s
VT_MAX = 400  # km/s
# integration parameters, in gigayears
STEPSIZE = 0.001  # Gyr
STEPS = 1500

# multiprocessing chunking size
CHUNKSIZE = 10

# ----------------------------------------------------

# helpful variables
X_RES = Y_RES = SIZE
SHAPE = (X_RES, Y_RES)
X_RANGE = (R_MIN, R_MAX)
Y_RANGE = (VT_MIN, VT_MAX)
EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)

# data arrays
# exclude the first point in X and Y, to avoid 0
T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr
X_ARR = np.linspace(R_MIN, R_MAX, X_RES + 1)[1:]  * u.kpc
Y_ARR = np.linspace(VT_MIN, VT_MAX, Y_RES + 1)[1:]  * u.km/u.s

# potential
MW_BARLESS =  [
    potential.NFWPotential(conc = 10, mvir = 1),
    potential.MiyamotoNagaiPotential(amp = 5e10 * u.solMass, a = 3 * u.kpc, b = 0.1 * u.kpc),
    potential.NonInertialFrameForce(Omega = 0 * u.km / u.s / u.kpc)
]
def compute_pixel(arg):
    i, r, j, v = arg
    initial_condition = [
        r, 
        0 * u.km / u.s, 
        v, 
        0 * u.kpc, 
        0 * u.km / u.s, 
        0 * u.deg
    ]
    o = orbit.Orbit(initial_condition)
    o.integrate(T_ARR, MW_BARLESS, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    return i, j, tess.area


def main():
    image = np.zeros(SHAPE)
    pixels = [(i, x, j, y) for i, x in enumerate(X_ARR) for j, y in enumerate(Y_ARR)]
    with Pool() as p:
        image_data = [(i, j, value) for i, j, value in tqdm(p.imap_unordered(compute_pixel, pixels, CHUNKSIZE), total=image.size)]

    # construct image
    for i, j, value in image_data:
        image[i, j] = value

    fig, ax = plt.subplots(figsize = (10, 10))
    ax.imshow(image.T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
    plt.show()

if __name__ == '__main__':
    main()