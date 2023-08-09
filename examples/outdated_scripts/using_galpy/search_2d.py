import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from utils import example, main

mw = potential.MWPotential2014
axsymm = [
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
]
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
        omegab = 2
    ),
    potential.NonInertialFrameForce(
        Omega = 2,
    )
]

@example()
def default_single():
    p = rotbar
    ts = np.linspace(0., 4., 2001) * u.Gyr

    def tessellation_area(x):
        o = orbit.Orbit([
            x[0] * u.kpc, 
            x[1] * u.km/u.s, 
            x[2] * u.km/u.s, 
            0 * u.kpc, 
            0 * u.km/u.s, 
            0 * u.deg
        ])
        o.integrate(ts, p, method='dopr54_c')
        line.set_xdata(o.x(o.t))
        line.set_ydata(o.y(o.t))
        fig.canvas.draw()
        fig.canvas.flush_events()
        tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
        print(x, tess.area)
        return tess.area

    x0 = [
        4 * np.random.random() + 1, 
        0 * np.random.random(), 
        -150 * np.random.random()
    ]
    # x0 = [3.0011066806433253, 4.649739534004408, 81.44804218028185]
    o = orbit.Orbit([
        x0[0] * u.kpc, 
        x0[1] * u.km/u.s, 
        x0[2] * u.km/u.s, 
        0 * u.kpc, 
        0 * u.km/u.s, 
        0 * u.deg
    ])
    o.integrate(ts, p, method='dopr54_c')

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(o.x(o.t), o.y(o.t))
    res = minimize(tessellation_area, x0, tol=0.01)
    

    x = res.x
    o = orbit.Orbit([
        x[0] * u.kpc, 
        x[1] * u.km/u.s, 
        x[2] * u.km/u.s, 
        0 * u.kpc, 
        0 * u.km/u.s, 
        0 * u.deg
    ])
    o.integrate(ts, p, method='dopr54_c')
    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    print(list(x), tess.area)
    tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
    tess.plot_tessellation_trimming(plot_included=True, plot_removed=True, plot_points=False)


@example()
def default():
    p = rotbar
    ts = np.linspace(0., 4., 2001) * u.Gyr

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(np.linspace(-6, 6, 100), np.linspace(-6, 6, 100))

    def tessellation_area(x):
        o = orbit.Orbit([
            x[0] * u.kpc, 
            x[1] * u.km/u.s, 
            x[2] * u.km/u.s, 
            0 * u.kpc, 
            0 * u.km/u.s, 
            0 * u.deg
        ])
        o.integrate(ts, p, method='dopr54_c')
        line.set_xdata(o.x(o.t))
        line.set_ydata(o.y(o.t))
        fig.canvas.draw()
        fig.canvas.flush_events()
        tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
        # print(x, tess.area)
        return tess.area

    for i in range(100):
        x0 = [
            4 * np.random.random() + 1, 
            0 * np.random.random(), 
            -150 * np.random.random()
        ]
        o = orbit.Orbit([
            x0[0] * u.kpc, 
            x0[1] * u.km/u.s, 
            x0[2] * u.km/u.s, 
            0 * u.kpc, 
            0 * u.km/u.s, 
            0 * u.deg
        ])
        o.integrate(ts, p, method='dopr54_c')
        res = minimize(tessellation_area, x0, tol=0.005)
        print(f'result_factory("rotbar {i}", rotbar, {list(res.x)})  # area={res.fun}')



def result_factory(name, p, x):
    @example(name)
    def result():
        o = orbit.Orbit([
            x[0] * u.kpc, 
            x[1] * u.km/u.s, 
            x[2] * u.km/u.s, 
            0 * u.kpc, 
            0 * u.km/u.s, 
            0 * u.deg
        ])
        ts = np.linspace(0., 4., 2001) * u.Gyr
        print('integrating...')
        o.integrate(ts, p, progressbar=True)

        print('tessellating...')
        tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
        print(tess.area)
        tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
        tess.plot_tessellation_trimming(plot_included=True, plot_points=False)

result_factory('mw 1', mw, [7.387902096436617, 34.77474289793684, 119.10933426312562])

result_factory('mw 2', mw, [6.245025095997171, 2.0939772166354134, 138.10742721459795])


result_factory('halo disc 1', axsymm, [2.4567457203742658, -0.40508027759713644, 156.1012702837712])
result_factory('halo disc 2', axsymm, [5.3726763982219286, 39.558510442978125, 76.68996225979714])

result_factory('rotbar 1', rotbar, [3.0009271490587444, 4.658661889618397, 81.4502567318411])
result_factory('rotbar 2', rotbar, [4.727067718339408, 1.5026119050304916e-08, -41.01774744407833])

if __name__ == '__main__':
    main(default=default)