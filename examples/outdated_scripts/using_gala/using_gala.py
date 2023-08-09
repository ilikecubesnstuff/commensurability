
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

import gala.potential as gp
import gala.dynamics as gd

from superfreq import find_frequencies, closest_resonance, SuperFreq


# mw = gp.MilkyWayPotential()
# mw = gp.potential.BovyMWPotential2014()
# mw = gp.NFWPotential(m=1e12, r_s=20 * u.kpc)
mw = gp.MilkyWayPotential()

# w0 = gd.PhaseSpacePosition(
#     pos=[4, 0, 0] * u.kpc,
#     vel=[0, 97.7, 52.0] * u.km/u.s
# )

n_orbits = 10
pos = np.random.uniform(-5, 5, size=(3, n_orbits)) * u.kpc
print(pos)
vel = np.random.uniform(-100, 100, size=(3, n_orbits)) * u.km/u.s
w0 = gd.PhaseSpacePosition(pos=pos, vel=vel)

t = np.linspace(0, 2, 2001)
orbits = mw.integrate_orbit(w0, t=t*u.Gyr)
# orbit.plot_3d(['x', 'y', 'z'])
# plt.show()

# w = orbit.w()
# print(w)
# print(w.shape)
# print(len(t), len(w))

# freqs = find_frequencies(w, silently_fail=False)

sf = SuperFreq(t)
for orbit in orbits.orbit_gen():
    # print(orbit.w())
    w = orbit.w()
    # ntimes, ndim = w.shape
    fs = w[:3,:] + 1j*w[3:,:]
    # fs = [(w[:,i] + 1j*w[:,i+ndim//2]) for i in range(ndim//2)]
    # print(fs)
    freqs = sf.find_fundamental_frequencies(fs)
    # print(freqs)
    # print(freqs.fund_freqs)
    # print(freqs.fund_freq_amps)
    # print(freqs.freq_mode_table)
    # print(freqs.fund_freqs_idx)

    f1, f2, f3 = sorted(freqs.fund_freqs)

    print(f1/f2, f1/f3, f2/f3)

    # print(closest_resonance(freqs.fund_freqs))