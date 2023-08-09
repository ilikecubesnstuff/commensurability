import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from tqdm import tqdm

from utils import example, main


def create_image(potential, rlims, vlims, steps, tlims, tsteps, liveplot=True, filename=None):
    R = np.linspace(*rlims, steps) * u.kpc
    V = np.linspace(*vlims, steps) * u.km/u.s
    T = np.linspace(*tlims, tsteps) * u.Gyr

    image = np.zeros(shape=(R.size, V.size))
    if liveplot:
        plt.ion()
        fig, (ax_image, ax_orbit) = plt.subplots(1, 2, figsize=(15, 6), width_ratios = [8, 7])
        phase_slice = ax_image.imshow(image, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=(*vlims, *rlims), aspect=50)
        ax_image.set_xlabel('V')
        ax_image.set_ylabel('R')
        fig.colorbar(phase_slice, ax=ax_image)
        trajectory, = ax_orbit.plot([0, 1], [0, 1])

    for i, r in tqdm(enumerate(R), total=R.size):
        for j, v in enumerate(V):
            initial_condition = [
                r, 
                0 * u.km / u.s, 
                v, 
                0 * u.kpc, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            o = orbit.Orbit(initial_condition)
            o.integrate(T, potential, method='dopr54_c')

            tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
            area = tess.area
            image[i, j] = area

            if liveplot:
                phase_slice.set_data(image)
                ax_image.set_title(f'{r=:0.4f}, {v=:0.2f}')
                X = o.x(o.t)
                Y = o.y(o.t)
                trajectory.set_xdata(X)
                trajectory.set_ydata(Y)
                trajectory.set_color((area, 1-area, 0))
                Xrange = max(abs(X))
                Yrange = max(abs(Y))
                ax_orbit.set_xlim([-Xrange, Xrange])
                ax_orbit.set_ylim([-Yrange, Yrange])
                ax_orbit.set_title(f'{area = }')
                fig.canvas.draw()
                fig.canvas.flush_events()

    filename = filename or 'Untitled.txt'
    np.savetxt(filename, image, header=f'{rlims=}, {vlims=}, {tlims=}')
    return image


@example(default=True)
def image():
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
        potential.SoftenedNeedleBarPotential(
            amp = 10e9 * u.solMass,
            a = 1.5 * u.kiloparsec,
            b = 0 * u.kiloparsec,
            c = 0.5 * u.kiloparsec,
            omegab = 2
        ),
        potential.NonInertialFrameForce(
            Omega = 2,
        )
    ]
    p = potential.MWPotential2014
    img = create_image(p, [0.02, 5], [1, 250], 250, [0, 1.2], 4001, liveplot=True, filename='MW_slice.txt')
    if plt.isinteractive:
        plt.ioff()
    plt.figure()
    plt.imshow(img)
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