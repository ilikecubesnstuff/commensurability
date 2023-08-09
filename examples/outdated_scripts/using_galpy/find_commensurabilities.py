import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from utils import example, main


@example()
def default():
    p = potential.MWPotential2014
    ts = np.linspace(0., 4., 2001) * u.Gyr

    def tessellation_volume(x):
        o = orbit.Orbit([
            x[0] * u.kpc, 
            x[1] * u.km/u.s, 
            x[2] * u.km/u.s, 
            x[3] * u.kpc, 
            x[4] * u.km/u.s, 
            x[5] * u.deg
        ])
        o.integrate(ts, p)
        tess = Tessellation.from_galpy_orbit(o, trim=40)
        print(x, tess.volume)
        return tess.volume

    # volume = 0
    # while volume > 0.05:
    x0 = [
        8 * np.random.random(), 
        50 * np.random.random(), 
        200 * np.random.random(), 
        3 * np.random.random(), 
        100 * np.random.random(), 
        2 * np.pi * np.random.random()
    ]
        # volume = tessellation_volume(x0)
    print('suitable orbit found')
    res = minimize(tessellation_volume, x0)

    x = res.x
    o = orbit.Orbit([
        x[0] * u.kpc, 
        x[1] * u.km/u.s, 
        x[2] * u.km/u.s, 
        x[3] * u.kpc, 
        x[4] * u.km/u.s, 
        x[5] * u.deg
    ])
    o.integrate(ts, p)
    tess = Tessellation.from_galpy_orbit(o, trim=40)
    print(list(x), tess.volume)
    tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
    tess.plot_tessellation_trimming(plot_included=True, plot_removed=True, plot_points=False)


N = 1
def result_factory(name, x):
    @example(name)
    def result():
        p = potential.MWPotential2014
        o = orbit.Orbit([
            x[0] * u.kpc, 
            x[1] * u.km/u.s, 
            x[2] * u.km/u.s, 
            x[3] * u.kpc, 
            x[4] * u.km/u.s, 
            x[5] * u.deg
        ])
        ts = np.linspace(0., 4., 2001) * u.Gyr
        print('integrating...')
        o.integrate(ts, p, progressbar=True)

        print('tessellating...')
        tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y', 'z'), trim=40)
        print(tess.volume)
        tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
        tess.plot_tessellation_trimming(plot_included=True, plot_removed=True, plot_points=False)

# @example('result 1')
# def result_1():
#     p = potential.MWPotential2014
#     o = orbit.Orbit([
#         5.16267744 * u.kpc, 
#         28.2023926 * u.km/u.s, 
#         111.60110557 * u.km/u.s, 
#         -19.36622094 * u.kpc, 
#         69.49144288 * u.km/u.s, 
#         4.75763285 * u.deg
#     ])
#     ts = np.linspace(0., 4., 2001) * u.Gyr
#     o.integrate(ts, p, progressbar=True)

#     tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y', 'z'), trim=40)
#     print(tess.volume)
#     tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
#     tess.plot_tessellation_trimming(plot_included=True, plot_points=False)

result_factory('result 1', [
    5.16267744,
    28.2023926,
    111.60110557,
    -19.36622094,
    69.49144288,
    4.75763285,
])

result_factory('result 2', [
    3.20029085e+00,
    8.44522675e-01,
    1.82376033e+02,
    2.60715080e-02,
    3.69750704e+01,
    9.08234059e-01,
])

result_factory('result 3', [1.8411202992209519, 31.938349071001934, 25.280339995509326, 0.03716018654030141, 1.1685548344980239, 3.0980006675330474])

result_factory('result 4', [2.1285241550662986, 45.66087400417824, 20.116670317395492, 0.09699251773648941, 64.99513858937948, 1.6060102856848852])

result_factory('result 5', [
    9.78054410e-09,
    2.73997603e+00,
    1.45599093e+02,
    1.77533681e+00,
    2.60821839e+01,
    6.27563272e-01,
])

if __name__ == '__main__':
    main(default=default)