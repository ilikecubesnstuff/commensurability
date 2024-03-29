import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

# galpy imports
from galpy import orbit as o
from galpy import potential as p

# defining the potential
omega = 30 * u.km / u.s / u.kpc
halo = p.NFWPotential(conc=10, mvir=1)
disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = p.SoftenedNeedleBarPotential(
    amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega
)
rotating = p.NonInertialFrameForce(Omega=omega)
pot = [halo, disc, bar, rotating]


# performing orbit integration
ts = np.linspace(0, 2, 501) * u.Gyr
ic = [1.5 * u.kpc, 255 * u.km / u.s, 0 * u.km / u.s, 1 * u.kpc, 0 * u.km / u.s, 0 * u.deg]
orbit = o.Orbit(ic)
orbit.integrate(ts, pot, method="dopr54_c", progressbar=True)
orbit.plot3d(d1="x", d2="y", d3="z")
plt.xlim([-7, 7])
plt.ylim([-7, 7])
plt.show()
