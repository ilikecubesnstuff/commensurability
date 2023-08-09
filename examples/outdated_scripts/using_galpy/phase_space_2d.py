from itertools import product
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from utils import example, main


rotbar = [
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
        omegab = 30 * u.km / u.s / u.kiloparsec,
    ),
    potential.NonInertialFrameForce(
        Omega = 30 * u.km / u.s / u.kiloparsec,
    )
]


@example()
def plot_1():
    img = np.loadtxt('rv_space.txt')
    plt.imshow(1-img, origin='lower', extent=(0.98, 5.02, 48.5, 351.5), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_2():
    img = np.loadtxt('rv_space_1.txt')
    plt.imshow(1-img, origin='lower', extent=(2.5965, 3.3035, 179.75, 230.25), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_3():
    img = np.loadtxt('rv_space_2.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_4():
    img = np.loadtxt('rv_space_3.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_5():
    img = np.loadtxt('rv_space_4.txt')
    plt.imshow(1-img, origin='lower', extent=(2, 4, 200, 400), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_6():
    img = np.loadtxt('rv_space_5.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_7():
    img = np.loadtxt('rv_space_6.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_8():
    img = np.loadtxt('rv_space_7.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_9():
    img = np.loadtxt('rv_space_8.txt')
    plt.imshow(1-img, origin='lower', extent=(3.14975, 3.35125, 205 - 0.75/8, 220 + 0.75/8), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_10():
    img = np.loadtxt('rv_space_9.txt')
    plt.imshow(1-img, origin='lower', extent=(0.1, 4, 20, 400), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()

@example()
def plot_11():
    img = np.loadtxt('rv_space_10.txt')
    plt.imshow(1-img, origin='lower', extent=(0.995, 2.005, 299.5, 400.5), aspect='auto', cmap='inferno')
    plt.colorbar()
    plt.show()


@example(default=True)
def brute_force(P = rotbar, display=True, filename='rv_space_11.txt'):
    R = np.linspace(1, 2, 101) * u.kpc
    V = np.linspace(300, 400, 101) * u.km / u.s
    T = np.linspace(0, 2, 1001) * u.Gyr

    with open(filename, 'a') as f:
        f.write(f'# {R}')
        f.write(f'# {V}')

    if display:
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([0, 1], [0, 1])

    img = []
    for r in R:
        row = []
        for v in tqdm(V, desc=f'{r = :0.5f}'):
            initial_condition = [
                r, 
                0 * u.km / u.s, 
                v, 
                0 * u.kpc, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            o = orbit.Orbit(initial_condition)
            o.integrate(T, P, method='dopr54_c')

            tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
            area = tess.area
            row.append(area)

            if display:
                X = o.x(o.t)
                Y = o.y(o.t)
                line.set_xdata(X)
                line.set_ydata(Y)
                line.set_color((area, 1-area, 0))
                ax.set_xlim([min(X), max(X)])
                ax.set_ylim([min(Y), max(Y)])
                ax.set_title(f'{area = }')
                fig.canvas.draw()
                fig.canvas.flush_events()
        img.append(row)
    np.savetxt(filename, img, header=f'R = {R}, V = {V}')


if __name__ == '__main__':
    main()