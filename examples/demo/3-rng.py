import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

# galpy imports
from galpy import orbit as o
from galpy import potential as p

# package imports
from tessellation import Tessellation

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
ic = [
    np.random.uniform(0, 5) * u.kpc,
    0 * u.km / u.s,
    np.random.uniform(-200, 200) * u.km / u.s,
    np.random.uniform(-3, 3) * u.kpc,
    0 * u.km / u.s,
    0 * u.deg,
]
orbit = o.Orbit(ic)
orbit.integrate(ts, pot, method="dopr54_c", progressbar=True)
orbit.plot3d(d1="x", d2="y", d3="z")
# plt.xlim([-7, 7])
# plt.ylim([-7, 7])
plt.show()

# tessellation
R, vR, vT, z, vz, phi = orbit.getOrbit().T
x = R * np.cos(phi)
y = R * np.sin(phi)
points = np.array([x, y, z]).T
tess = Tessellation(points, verbosity=1)
print(f"{tess.volume = }")
tess.plot(plot_included=True, plot_removed=True, plot_points=True)
