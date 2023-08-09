from itertools import product

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from tqdm import tqdm

from utils import example, main

from multiprocessing import Pool


def compute_orbit(ic, p, tlims, tsteps):
    ts = np.linspace(*tlims, tsteps) * u.Gyr
    o = orbit.Orbit(ic)
    o.integrate(ts, p, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'), trim=None)
    return tess.points.T


@example(default=True)
def default():
    filename = 'MW_slice.txt'
    img = np.loadtxt(filename).T

    with open(filename) as f:
        header = f.readline()
    header = header[2:].split(', ')
    rlims = eval((header[0] + ', ' + header[1]).split('=')[1])
    vlims = eval((header[2] + ', ' + header[3]).split('=')[1])
    tlims = eval((header[4] + ', ' + header[5]).split('=')[1])
    aspect = (rlims[1] - rlims[0]) / (vlims[1] - vlims[0])
    # rlims = [0.004, 2]
    # vlims = [300.6, 600]
    # tlims=[0, 1.5]
    tsteps=1501

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
            omegab = 30 * u.km / u.s / u.kpc
        ),
        potential.NonInertialFrameForce(
            Omega = 30 * u.km / u.s / u.kpc
        )
    ]
    p = potential.MWPotential2014

    # plt.ion()
    fig, (ax_phase, ax_orbit) = plt.subplots(1, 2)
    plt_img = ax_phase.imshow(img, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=(*rlims, *vlims), aspect=aspect)
    plt_line, = ax_orbit.plot([0], [0], '-')

    def on_click(event):
        if event.button == 3:
            plt_line.set_xdata([0])
            plt_line.set_ydata([0])
        if event.button == 1:
            print(event.xdata, event.ydata)
            ic = [
                event.xdata * u.kpc,
                0 * u.km / u.s, 
                event.ydata * u.km / u.s, 
                0 * u.kpc, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            X, Y = compute_orbit(ic, p, tlims, tsteps)
            plt_line.set_xdata(X)
            plt_line.set_ydata(Y)
            Xrange = max(abs(X))
            Yrange = max(abs(Y))
            ax_orbit.set_xlim([-Xrange, Xrange])
            ax_orbit.set_ylim([-Yrange, Yrange])
            ax_orbit.set_title(f'{event.ydata}, {event.xdata}')
            fig.canvas.draw()
            fig.canvas.flush_events()

    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()

# @example()
# def timestep_images():

if __name__ == '__main__':
    main()