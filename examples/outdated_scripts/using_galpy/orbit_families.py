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

def get_area_from(initial_condition, potential=rotbar, plot=False):
    o = orbit.Orbit(initial_condition)
    ts = np.linspace(0, 2, 4001) * u.Gyr
    o.integrate(ts, potential, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    if plot:
        tess.plot_tessellation_trimming(plot_points=True, plot_included=False)
        tess.plot_tessellation_trimming(plot_points=False, plot_included=True)
    return tess.area


@example()
def plot():
    pass


@example()
def test():
    # start = 1.667999999999999927e+00+3.428000000000008640e+02j
    # start = 1.32 + 339.j
    # start = 1.50 + 340.j
    start = 1.97 + 317.j
    # start = 1.74 + 388.002j
    # start = 1.3164 + 338.68j
    start = 1.75 + 370j
    ic = [
        start.real * u.kpc, 
        0 * u.km / u.s, 
        start.imag * u.km / u.s, 
        0 * u.kpc, 
        0 * u.km / u.s, 
        0 * u.deg
    ]
    a = get_area_from(ic, plot=True)
    print(a)


@example(default=True)
def walk():
    start = 1.74 + 388.002j
    start = 1.97 + 317.j
    start = 1.50 + 340.j
    start = 1.32 + 339.j
    start = 1.3132 + 339.j
    start = 1.3164 + 338.685j
    start = 1.97 + 317.j
    # start = 1.75 + 375j
    start = 1.75 + 370j
    MAX_VISITED = 20000

    # visited = [start]
    # current = [start]
    # threshold = 1
    # while len(visited) < MAX_VISITED:
    #     temp = []
    #     for s in current:
    #         for ds in (0.0002, -0.0002, 0.005j, -0.005j):
    #             snew = s + ds
    #             if snew in visited:
    #                 continue
    #             if snew in current:
    #                 continue
    #             r = snew.real
    #             v = snew.imag
    #             ic = [
    #                 r * u.kpc, 
    #                 0 * u.km / u.s, 
    #                 v * u.km / u.s, 
    #                 0 * u.kpc, 
    #                 0 * u.km / u.s, 
    #                 0 * u.deg
    #             ]
    #             a = get_area_from(ic)
    #             print(a, snew)
    #             if a < threshold:
    #                 start = ic
    #                 temp.append(snew)
    #             visited.append(snew)
    #         else:
    #             continue
    #         break
    #     else:
    #         current = temp
    #         continue
    #     break
    # print('start area:', a)
    # return

    low = []
    low_threshold = 0.1
    family = [start]
    visited = [start]
    current = [start]
    threshold = 0.25
    while len(visited) < MAX_VISITED:
        temp = []
        for s in current:
            for ds in (0.0002, -0.0002, 0.005j, -0.005j):
                snew = s + ds
                if snew in visited:
                    continue
                if snew in current:
                    continue
                r = snew.real
                v = snew.imag
                ic = [
                    r * u.kpc, 
                    0 * u.km / u.s, 
                    v * u.km / u.s, 
                    0 * u.kpc, 
                    0 * u.km / u.s, 
                    0 * u.deg
                ]
                a = get_area_from(ic)
                # print(a, snew)
                if a < threshold:
                    # threshold = max((threshold + a)/2, 0.1)
                    if a < low_threshold:
                        print('ASDJFLKASJDFLKJASFLASDJAFA', ic)
                        low.append(snew)
                    else:
                        family.append(snew)
                    temp.append(snew)
                visited.append(snew)
        print('states visited:', len(visited))
        if len(temp) == 0:
            break
        current = temp

    # r, v = 2.4, 326
    # MAX_VISITED = 100

    # family = [
    #     (r, v),
    # ]
    # visited = [
    #     (r, v),
    # ]
    # current = [
    #     (r, v),
    # ]
    # while len(visited) < MAX_VISITED:
    #     print(visited, MAX_VISITED)
    #     removed = []
    #     for r, v in current:
    #         for dr, dv in (
    #             ( 0.01,  0),
    #             (-0.01,  0),
    #             ( 0  ,  0.1),
    #             ( 0  , -0.1),
    #         ):
    #             rnew = r + dr
    #             vnew = v + dv
    #             if (rnew, vnew) in visited:
    #                 continue
    #             if (rnew, vnew) in current:
    #                 continue
    #             ic = [
    #                 rnew * u.kpc, 
    #                 0 * u.km / u.s, 
    #                 vnew * u.km / u.s, 
    #                 0 * u.kpc, 
    #                 0 * u.km / u.s, 
    #                 0 * u.deg
    #             ]
    #             if get_area_from(ic) < 0.1:
    #                 print((rnew, vnew))
    #                 family.append((rnew, vnew))
    #                 current.add((rnew, vnew))
    #             visited.append((rnew, vnew))
    #         removed.append((r, v))
    #         if len(current) == 0:
    #             break
    #     for pair in removed:
    #         current.remove(pair)
    
    # R, V = np.array(family).T
    np.savetxt('family.txt', family)
    np.savetxt('low.txt', low)

    R = [c.real for c in family]
    V = [c.imag for c in family]
    plt.plot(R, V, 'ro')

    R = [c.real for c in low]
    V = [c.imag for c in low]
    plt.plot(R, V, 'go')
    plt.show()
    print(family)
    return family


if __name__ == '__main__':
    main()