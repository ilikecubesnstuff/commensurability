import numpy as np
import astropy.units as u
import galpy.potential as p
import galpy.orbit as o

from commensurability.tessellation import Tessellation


pot = p.MWPotential2014
orbit = o.Orbit([
    8 * np.random.random() * u.kpc, 
    50 * np.random.random() * u.km/u.s, 
    200 * np.random.random() * u.km/u.s, 
    3 * np.random.random() * u.kpc, 
    100 * np.random.random() * u.km/u.s, 
    2 * np.pi * np.random.random() * u.deg
])
ts = np.linspace(0., 2., 501) * u.Gyr
orbit.integrate(ts, pot, progressbar=True)

tess = Tessellation.from_galpy_orbit(orbit, dims=('x', 'y', 'z'))
print(tess.volume)
tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
tess.plot_tessellation_trimming(plot_included=True, plot_points=False)