import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt

from galpy import potential, orbit

DIMENSIONLESS = u.s/u.s

POTENTIAL = potential.MWPotential2014

n_orbits = 10
ics = [
    np.random.uniform(5, 8, n_orbits) * u.kpc,
    np.random.uniform(0, 0, n_orbits) * u.km/u.s,
    np.random.uniform(100, 150, n_orbits) * u.km/u.s,
    np.random.uniform(0, 5, n_orbits) * u.kpc,
    np.random.uniform(0, 0, n_orbits) * u.km/u.s,
    np.random.uniform(0, 360, n_orbits) * u.deg
]
ts = np.linspace(0, 2, 1001) * u.Gyr

o = orbit.Orbit(ics)
o.integrate(ts, pot=POTENTIAL)

# o.plot()
# plt.show()

# for orbit in o:
#     print(orbit.getOrbit())

data = o.getOrbit()
print(data.shape, data.size, data.dtype)

omega = 10 * u.km/u.s/u.kpc
o = o[0]

o.turn_physical_on()
phi_offset = omega * ts
print(phi_offset.to(DIMENSIONLESS))

R = o.R()
phi = o.phi() + phi_offset.to(DIMENSIONLESS)
print(o.phi(ts))
print(phi)
