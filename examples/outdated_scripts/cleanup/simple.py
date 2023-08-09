from tqdm import tqdm
from math import prod
from itertools import islice

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool

import h5py




def clump(iterable, size=10):
    while True:
        c = tuple(islice(iterable, size))
        if not c:
            return
        yield c


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]



SIZE = 100
ics = dict(
    R   = np.linspace(0, 10, SIZE + 1)[1:]  * u.kpc,
    vR  = np.linspace(0, 0, 1)  * u.km/u.s,
    vT  = np.linspace(0, 300, SIZE + 1)[1:]  * u.km/u.s,
    z   = np.linspace(1, 1, 1)  * u.kpc,
    vz  = np.linspace(0, 0, 1)  * u.km/u.s,
    phi = np.linspace(0, 0, 1)  * u.deg,
)
ts = np.linspace(0, 1, 501) * u.Gyr

DIMENSIONLESS = u.s/u.s
phi_offset = (omega * ts).to(DIMENSIONLESS)




CHUNKSIZE = 100

shape = (ics['R'].size, ics['vR'].size, ics['vT'].size, ics['z'].size, ics['vz'].size, ics['phi'].size)


image = np.zeros(shape)

indices = np.ndindex(shape)
chunked_indices = clump(indices, size=CHUNKSIZE)
for i_chunk in tqdm(chunked_indices, total=prod(shape)//CHUNKSIZE):
    i_chunk = np.array(i_chunk)
    ic = [arr[i] for i, arr in zip(i_chunk.T, ics.values())]
    os = orbit.Orbit(ic)
    os.integrate(ts, pot, progressbar=False)
    os.turn_physical_on()
    for i, o in zip(i_chunk, os):
        R = o.R(ts)
        phi = o.phi(ts) + phi_offset
        # print(phi)
        x = R * np.cos(phi.value)
        y = R * np.sin(phi.value)
        z = o.z(ts)
        points = np.array([x, y, z]).T
        tess = Tessellation(points)
        image[tuple(i)] = tess.volume

newshape = tuple(s for s in shape if s != 1)
image = image.reshape(newshape)


np.save('image.npy', image)
with h5py.File('image.hdf5', 'w') as f:
    dset = f.create_dataset('image', data=image)
    dset.attrs['R_min'] = np.min(ics['R'])
    dset.attrs['R_max'] = np.max(ics['R'])
    dset.attrs['vR_min'] = np.min(ics['vR'])
    dset.attrs['vR_max'] = np.max(ics['vR'])
    dset.attrs['vT_min'] = np.min(ics['vT'])
    dset.attrs['vT_max'] = np.max(ics['vT'])
    dset.attrs['z_min'] = np.min(ics['z'])
    dset.attrs['z_max'] = np.max(ics['z'])
    dset.attrs['vz_min'] = np.min(ics['vz'])
    dset.attrs['vz_max'] = np.max(ics['vz'])
    dset.attrs['phi_min'] = np.min(ics['phi'])
    dset.attrs['phi_max'] = np.max(ics['phi'])


plt.imshow(image.T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=(0, 10, 0, 600), aspect=10/600)
plt.show()








exit()



SIZE = 10
ics = {
    'R': np.linspace(0, 10, SIZE + 1)[1:] * u.kpc,
    'vR': np.array([0]) * u.km/u.s,
    'vT': np.linspace(0, 300, SIZE + 1)[1:] * u.km/u.s,
    'z': np.array([1]) * u.kpc,
    'vz': np.array([0]) * u.km/u.s,
    'phi': np.array([0]) * u.deg,
}
ts = np.linspace(0, 1, 501) * u.Gyr




def clump(it, chunksize=10):
    chunk = []
    for i, obj in enumerate(it):
        chunk.append(obj)
        if len(chunk) == chunksize:
            yield tuple(chunk)
            chunk = []
    if chunk:
        yield tuple(chunk)



CHUNKSIZE = 10

shape = (ics['R'].size, ics['vR'].size, ics['vT'].size, ics['z'].size, ics['vz'].size, ics['phi'].size)

print('starting loop')

image = np.zeros(shape)
it = np.ndindex(shape)
it = clump(it, chunksize=CHUNKSIZE)
for inds in tqdm(it, total=prod(shape)//CHUNKSIZE):
    # print('new loop')
    # print(inds)
    inds = np.array(inds).T
    ic = [arr[i] for i, arr in zip(inds, ics.values())]
    # print(ic)
    os = orbit.Orbit(ic)
    os.integrate(ts, pot, progressbar=False)
    # os.plot()
    # plt.show()
    # os.plot(d1='x', d2='y')
    # plt.show()
    # break
    # print('integration done')

    for i, o in zip(inds.T, os):
        # print(i)
        tess = Tessellation.from_galpy_orbit(o)
        # tess.plot_tessellation_trimming()
        # print(image[tuple(i)])
        image[tuple(i)] = tess.volume
    # print(image)
    # print('volume recorded')

print('loop done')


newshape = tuple(s for s in shape if s != 1)
image = image.reshape(newshape)

# np.save('image.npy', image)

plt.imshow(image.T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=(0, 10, 0, 600), aspect=10/600)
plt.show()


exit()




SIZE = 5

# ics = {
#     'R': np.linspace(0, 10, SIZE + 1)[1:],
#     'vR': np.array([0]),
#     'vT': np.linspace(0, 600, SIZE + 1)[1:],
#     'z': np.array([1]),
#     'vz': np.array([0]),
#     'phi': np.array([0]),
# }
ics = {
    'R': np.linspace(0, 10, SIZE + 1)[1:] * u.kpc,
    'vR': np.array([0]) * u.km/u.s,
    'vT': np.linspace(0, 600, SIZE + 1)[1:] * u.km/u.s,
    'z': np.array([1]) * u.kpc,
    'vz': np.array([0]) * u.km/u.s,
    'phi': np.array([0]) * u.deg,
}
ts = np.linspace(0, 2, 1001) * u.Gyr


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]


shape = (ics['R'].size, ics['vR'].size, ics['vT'].size, ics['z'].size, ics['vz'].size, ics['phi'].size)

print('starting loop')

image = np.zeros(shape)
for inds in tqdm(np.ndindex(shape), total=prod(shape)):
    ic = [arr[i] for i, arr in zip(inds, ics.values())]
    o = orbit.Orbit(ic)
    o.integrate(ts, pot)

    tess = Tessellation.from_galpy_orbit(o)
    image[inds] = tess.volume

print('loop done')


newshape = tuple(s for s in shape if s != 1)
image = image.reshape(newshape)

plt.imshow(image)
plt.show()

exit()



SIZE = 10

R = np.linspace(0, 10, SIZE + 1)[1:]
vR = np.array([0])
vT = np.linspace(0, 600, SIZE + 1)[1:]
z = np.array([1])
vz = np.array([0])
phi = np.array([0])

# ------

shape = (R.size, vR.size, vT.size, z.size, vz.size, phi.size)
# Ri, vRi, vTi, zi, vzi, phii = np.indices(shape)
# R = R[Ri]
# vR = vR[vRi]
# vT = vT[vTi]
# z = z[zi]
# vz = vz[vzi]
# phi = phi[phii]



# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]



image = np.zeros(shape)
# find some clever way to loop over everything while being able to extract the indices for the image pixel
for inds in np.ndindex(shape):
    pass


exit()


SIZE = 10

ts = np.linspace(0, 2, 1001) * u.Gyr
R = np.linspace(0, 10, SIZE + 1)[1:] * u.kpc
vT = np.linspace(0, 500, SIZE + 1)[1:] * u.km/u.s

vR = np.array([0]) * u.km/u.s
z = np.array([1]) * u.kpc
vz = np.array([0]) * u.km/u.s
phi = np.array([0]) * u.deg


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]


# helpful quantities
shape = (R.size, vR.size, vT.size, z.size, vz.size, phi.size)

ics = np.array(tuple(product(R, vR, vT, z, vz, phi)))
print(ics)
# os = orbit.Orbit(tuple(product(R, vR, vT, z, vz, phi)))
# print(os.shape)


exit()

# square image, size of one side in pixels
SIZE = 100
# omega parameter values, in kilometers per second per kiloparsec
OMEGA_MIN = 0  # km/s/kpc
OMEGA_MAX = 40  # km/s/kpc
FRAMES = 41

# range of R (cylindrical coordinates), in kiloparsecs
R_MIN = 0  # kpc
R_MAX = 8  # kpc
# range of tangential velocity, in kilometers per second
VT_MIN = 0  # km/s
VT_MAX = 400  # km/s
# integration parameters, in gigayears
STEPSIZE = 0.001  # Gyr
STEPS = 1500

# name
NAME = 'MORE_MW_BAR'
# save location
FILENAME = f'{NAME}_over_OMEGA_{OMEGA_MIN}-{OMEGA_MAX}__R_{R_MIN}-{R_MAX}__VT_{VT_MIN}-{VT_MAX}__INT_{STEPSIZE}_{STEPS}.npy'

# multiprocessing chunking size
CHUNKSIZE = 100

# ----------------------------------------------------

# helpful variables
X_RES = Y_RES = SIZE
SHAPE = (FRAMES, X_RES, Y_RES)
X_RANGE = (R_MIN, R_MAX)
Y_RANGE = (VT_MIN, VT_MAX)
EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)


# data arrays
# exclude the first point in X and Y, to avoid 0
OMEGA_ARR = np.linspace(OMEGA_MIN, OMEGA_MAX, FRAMES)  * u.km/u.s/u.kpc
T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr
X_ARR = np.linspace(R_MIN, R_MAX, X_RES + 1)[1:]  * u.kpc
Y_ARR = np.linspace(VT_MIN, VT_MAX, Y_RES + 1)[1:]  * u.km/u.s

# potentials
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
rotpot_factory = lambda omega: [
    halo,
    disc,
    potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
    potential.NonInertialFrameForce(Omega = omega)
]
potentials = [rotpot_factory(omega) for omega in OMEGA_ARR]
def compute_pixel(arg):
    frame, pot, i, r, j, v = arg
    initial_condition = [
        r, 
        0 * u.km / u.s, 
        v, 
        0 * u.kpc, 
        0 * u.km / u.s, 
        0 * u.deg
    ]
    o = orbit.Orbit(initial_condition)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    return frame, i, j, tess.area


def main():
    cube = np.zeros(SHAPE)
    pixels = [(frame, pot, i, x, j, y) for frame, pot in enumerate(potentials) for i, x in enumerate(X_ARR) for j, y in enumerate(Y_ARR)]
    with Pool() as p:
        image_data = [(frame, i, j, value) for frame, i, j, value in tqdm(p.imap_unordered(compute_pixel, pixels, CHUNKSIZE), total=cube.size)]

    # construct image
    for frame, i, j, value in image_data:
        cube[frame, i, j] = value

    np.save(FILENAME, cube)

    fig, ax = plt.subplots(figsize = (10, 10))
    ax.imshow(cube[0].T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
    plt.show()

if __name__ == '__main__':
    main()