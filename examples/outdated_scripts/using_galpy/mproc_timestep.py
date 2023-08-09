from itertools import product

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from tqdm import tqdm

from utils import example, main

from multiprocessing import Pool

P = [
    potential.NFWPotential(
        conc = 10,
        mvir = 1,
    ),
    potential.MiyamotoNagaiPotential(
        amp = 5e10 * u.solMass,
        a = 3 * u.kiloparsec,
        b = 0.1 * u.kiloparsec,
    ),
    potential.SoftenedNeedleBarPotential(
        amp = 10e9 * u.solMass,
        a = 1.5 * u.kiloparsec,
        b = 0 * u.kiloparsec,
        c = 0.5 * u.kiloparsec,
        omegab = 30 * u.km / u.s / u.kpc
    ),
    potential.NonInertialFrameForce(
        Omega = 30 * u.km / u.s / u.kpc
    )
]
P = potential.MWPotential2014
T = np.linspace(0, 1.2, 2001) * u.Gyr
def compute_pixel(arg):
    i, r, j, v = arg
    # if r > 8 * (1 - v/600):
    #     return 0
    initial_condition = [
        r * u.kpc,
        0 * u.km / u.s, 
        v * u.km / u.s, 
        0 * u.kpc, 
        0 * u.km / u.s, 
        0 * u.deg
    ]
    o = orbit.Orbit(initial_condition)
    # print(f'integrating {r=}, {v=}')
    o.integrate(T, P)

    # print(f'tessellating {r=}, {v=}')
    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    area = tess.area
    # print(f'completed {r=}, {v=}')
    return area


def create_image(potential, rlims, vlims, steps, tlims, tsteps, liveplot=True, filename=None):
    R = np.linspace(*rlims, steps)
    V = np.linspace(*vlims, steps)

    image = np.zeros(shape=(R.size, V.size))

    pixels = [(i, r, j, v) for i, r in enumerate(R) for j, v in enumerate(V)]
    with Pool() as p:
        image = [pixel for pixel in tqdm(p.imap(compute_pixel, pixels, chunksize=4), total=R.size*V.size)]
    image = np.array(image).reshape((R.size, V.size))

    filename = filename or 'Untitled.txt'
    np.savetxt(filename, image, header=f'{rlims=}, {vlims=}, {tlims=}')
    return image


@example(default=True)
def image():
    rlim = [0.02, 10]
    vlim = [1.2, 600]
    img = create_image(None, rlim, vlim, 500, [0, 2], 1501, liveplot=True, filename='MW_slice.txt')
    if plt.isinteractive:
        plt.ioff()
    plt.figure()
    plt.imshow(img.T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=(*vlim, *rlim), aspect=150)
    plt.colorbar()
    plt.show()


@example()
def timestep_images():
    p = [
        potential.NFWPotential(
            conc = 10,
            mvir = 1,
        ),
        potential.MiyamotoNagaiPotential(
            amp = 5e10 * u.solMass,
            a = 3 * u.kiloparsec,
            b = 0.1 * u.kiloparsec,
        ),
        # potential.SoftenedNeedleBarPotential(
        #     amp = 10e9 * u.solMass,
        #     a = 1.5 * u.kiloparsec,
        #     b = 0 * u.kiloparsec,
        #     c = 0.5 * u.kiloparsec,
        #     omegab = 2
        # ),
        # potential.NonInertialFrameForce(
        #     Omega = 2,
        # )
    ]
    img_args = dict(
        rlims = [0.05, 5],
        vlims = [2, 200],
        steps = 100
    )
    for trange in (1, 2, 4):
        for tsteps in (1001, 2001, 4001):
            print('running:', trange, tsteps)
            img = create_image(p, **img_args, tlims=[0, trange], tsteps=tsteps, filename=f'img_{trange}_{tsteps}.txt')
    if plt.isinteractive:
        plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()