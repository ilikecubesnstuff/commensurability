# this file has nothing to do with monte-carlo
# it is just frequency analysis but plotted with RGB

from __future__ import print_function
from itertools import product
from tqdm import tqdm
from time import time

import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u

import gala.potential as gp
import gala.dynamics as gd
from gala.units import galactic

from superfreq import find_frequencies, closest_resonance, SuperFreq

from commensurability.utils import clump


disk = gp.MiyamotoNagaiPotential(m=6E10*u.Msun,
                                 a=3.5*u.kpc, b=280*u.pc,
                                 units=galactic)
bar = gp.LongMuraliBarPotential(m=1E10*u.Msun, a=4*u.kpc,
                                b=0.8*u.kpc, c=0.25*u.kpc,
                                alpha=25*u.degree,
                                units=galactic)
halo = gp.NFWPotential(m=6E11*u.Msun, r_s=20.*u.kpc, units=galactic)
pot = gp.CCompositePotential()
pot['disk'] = disk
pot['halo'] = halo
pot['bar'] = bar

Om_bar = 30. * u.km/u.s/u.kpc
frame = gp.ConstantRotatingFrame(Omega=[0,0,Om_bar.value]*Om_bar.unit,
                                 units=galactic)
H = gp.Hamiltonian(potential=pot, frame=frame)


SIZE = 200
image = np.zeros((SIZE, SIZE, 3))


RMIN = 0
RMAX = 12
VMIN = 0
VMAX = 400

rs = np.linspace(RMIN, RMAX, SIZE + 1)[1:]
vs = np.linspace(VMIN, VMAX, SIZE + 1)[1:]

ri, vi = np.indices((SIZE, SIZE))
rs = rs[ri.flatten()]
vs = vs[vi.flatten()]

clumpsize = 50
rs = clump(rs, clumpsize)
vs = clump(vs, clumpsize)
CLUMPS = SIZE*SIZE//clumpsize

def ratio(f1, f2):
    return f1/f2 if f1 > f2 else f2/f1

counter = 0
for i, (rchunk, vchunk) in tqdm(enumerate(zip(rs, vs)), total=CLUMPS):
    TOTAL = len(rchunk)
    pos = np.array([
        np.array(rchunk),
        np.zeros(TOTAL),
        1 * np.ones(TOTAL),
    ]) * u.kpc
    vel = np.array([
        np.zeros(TOTAL),
        np.array(vchunk),
        np.zeros(TOTAL),
    ]) * u.km/u.s
    t = np.linspace(0, 2, 2001)

    start = time()
    ws = gd.PhaseSpacePosition(pos=pos, vel=vel)
    orbits = H.integrate_orbit(ws, t=t*u.Gyr)
    end = time()
    # print(end-start, 'integration time')


    sf = SuperFreq(t)
    # for i, orbit in tqdm(enumerate(orbits.orbit_gen()), desc=f'chunk {i}/{CLUMPS}', total=TOTAL):
    for orbit in orbits.orbit_gen():
        i = counter
        counter += 1
        # print(orbit)
        # orbit.plot_3d()
        # plt.show()
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

        j, i = divmod(i, SIZE)
        f1, f2, f3 = map(abs, freqs.fund_freqs)
        # print(f1, f2, f3)

        r = ratio(f1, f2)
        d = 2*abs(round(r) - r)
        image[i, j, 0] = 1-d if r<10 else 0

        r = ratio(f1, f3)
        d = 2*abs(round(r) - r)
        image[i, j, 1] = 1-d if r<10 else 0

        r = ratio(f2, f3)
        d = 2*abs(round(r) - r)
        image[i, j, 2] = 1-d if r<10 else 0
        # exit()

np.save('image.npy', image)

plt.imshow(image, origin='lower', extent=(RMIN, RMAX, VMIN, VMAX), aspect=(RMAX-RMIN)/(VMAX-VMIN))
plt.show()