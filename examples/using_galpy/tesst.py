import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt

import galpy.potential as p
import galpy.orbit as o

from commensurability.tessellation import Tessellation


pot = p.MWPotential2014
ts = np.linspace(0., 2., 501) * u.Gyr
ic = [
    8 * np.random.random() * u.kpc,
    50 * np.random.random() * u.km/u.s,
    200 * np.random.random() * u.km/u.s,
    3 * np.random.random() * u.kpc,
    100 * np.random.random() * u.km/u.s,
    2 * np.pi * np.random.random() * u.deg
]
# ic = [
#     0.46502006 * u.kpc,
#     45.21232635 * u.km/u.s,
#     119.501485 * u.km/u.s,
#     # 3 * np.random.random() * u.kpc,
#     # 100 * np.random.random() * u.km/u.s,
#     0.81265312 * u.deg
# ]
# ic = [
#     8. * u.kpc,
#     0. * u.km/u.s,
#     0. * u.km/u.s,
#     # 3 * np.random.random() * u.kpc,
#     # 100 * np.random.random() * u.km/u.s,
#     0. * u.deg
# ]
print(ic)
orbit = o.Orbit(ic)
orbit.integrate(ts, pot, progressbar=True)

tess = Tessellation(orbit, ['x', 'y'])
print(tess, tess.measure < 0.01)

fig = plt.figure()
tess.plot(fig, plot_removed=True)
plt.show()