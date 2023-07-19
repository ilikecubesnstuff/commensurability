import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from utils import example, main

@example('MW random')
def random_MW_orbit_3d():
    p = potential.MWPotential2014
    o = orbit.Orbit([ # some kinda 3D resonance
        8 * np.random.random() * u.kpc, 
        50 * np.random.random() * u.km/u.s, 
        200 * np.random.random() * u.km/u.s, 
        3 * np.random.random() * u.kpc, 
        100 * np.random.random() * u.km/u.s, 
        2 * np.pi * np.random.random() * u.deg
    ])
    ts = np.linspace(0.,4.,1001) * u.Gyr
    o.integrate(ts, p, progressbar=True)

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y', 'z'))
    tess.calculate_trimming(axis_ratio=10)
    print(tess.volume)
    tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
    tess.plot_tessellation_trimming(plot_included=True, plot_points=False)

@example()
def commensurate():
    p = potential.MWPotential2014
    o = orbit.Orbit([ # some kinda 3D resonance
        4. * u.kpc, 
        0.0 * u.km/u.s, 
        97.7 * u.km/u.s, 
        0.0 * u.kpc, 
        52.0 * u.km/u.s, 
        0.0 * u.deg
    ])

    ts = np.linspace(0.,10.,10001)*u.Gyr
    o.integrate(ts, p, progressbar=True)

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y', 'z'))
    tess.calculate_trimming(axis_ratio=10)
    print(tess.volume)
    tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
    tess.plot_tessellation_trimming(plot_included=True, plot_points=False)


if __name__=='__main__':
    main(default=random_MW_orbit_3d)