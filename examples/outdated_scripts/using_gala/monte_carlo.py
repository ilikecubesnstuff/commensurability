from itertools import product
from tqdm import tqdm
from time import time

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

import gala.potential as gp
import gala.dynamics as gd

from superfreq import find_frequencies, closest_resonance, SuperFreq


mw = gp.MilkyWayPotential()


SIZE = 100
image = np.zeros((SIZE, SIZE, 3))


rs = np.linspace(0, 10, SIZE + 1)[1:]
vs = np.linspace(0, 600, SIZE + 1)[1:]

ri, vi = np.indices((SIZE, SIZE))
rs = rs[ri.flatten()]
vs = vs[vi.flatten()]

TOTAL = SIZE * SIZE
pos = np.array([
    rs,
    np.zeros(TOTAL),
    2 * np.ones(TOTAL),
]) * u.kpc
vel = np.array([
    np.zeros(TOTAL),
    vs,
    np.zeros(TOTAL),
]) * u.km/u.s
t = np.linspace(0, 2, 2001)

start = time()
ws = gd.PhaseSpacePosition(pos=pos, vel=vel)
orbits = mw.integrate_orbit(ws, t=t*u.Gyr,)
end = time()
print(end-start, 'integration time')


sf = SuperFreq(t)
for i, orbit in tqdm(enumerate(orbits.orbit_gen()), total=TOTAL):
    w = orbit.w()
    fs = w[:3,:] + 1j*w[3:,:]
    try:
        freqs = sf.find_fundamental_frequencies(fs)
    except RuntimeError as e:
        print(e)
        continue
    except IndexError as e:
        print(fs[:2])
        print(e)
        continue
    # print(freqs)
    # print(freqs.fund_freqs)
    # print(freqs.fund_freq_amps)
    # print(freqs.freq_mode_table)
    # print(freqs.fund_freqs_idx)

    i, j = divmod(i, SIZE)
    f1, f2, f3 = sorted(freqs.fund_freqs)

    r = f1/f2
    d = 2*abs(round(r) - r)
    image[i, j, 0] = 1-d if r<10 else 0

    r = f1/f3
    d = 2*abs(round(r) - r)
    image[i, j, 1] = 1-d if r<10 else 0

    r = f2/f3
    d = 2*abs(round(r) - r)
    image[i, j, 2] = 1-d if r<10 else 0

plt.imshow(image, origin='lower', extent=(0, 8, 0, 400), aspect=8/400)
plt.show()