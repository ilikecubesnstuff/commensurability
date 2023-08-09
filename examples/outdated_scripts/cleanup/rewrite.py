from tqdm import tqdm
from itertools import product

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool

import h5py






SIZE = 10

R = np.linspace(0, 10, SIZE + 1)[1:] * u.kpc
vR = np.array([0]) * u.km/u.s
vT = np.linspace(0, 500, SIZE + 1)[1:] * u.km/u.s
z = np.array([1]) * u.kpc
vz = np.array([0]) * u.km/u.s
phi = np.array([0]) * u.deg
ts = np.linspace(0, 2, 1001) * u.Gyr


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]






def _eval(o):
    print('!')
    phi_offset = omega * ts

    R = o.R()
    phi = o.phi() + phi_offset.to(DIMENSIONLESS)
    z = o.z()
    points = np.array([R*np.cos(phi), R*np.sin(phi), z]).T

    tess = Tessellation(points)
    return tess.measure

def compute_pixel(data):
    print('.')
    inds = []
    ics = []
    for row in data:
        ind, ic = zip(*row)
        inds.append(ind)
        ics.append(ic)
    os = orbit.Orbit(ics)
    os.integrate(ts, pot)
    values = tuple(_eval(o) for o in os)
    return tuple(zip(inds, values))


DIMENSIONLESS = u.s/u.s


def clump(it, chunksize=10):
    chunk = []
    for i, obj in enumerate(it):
        chunk.append(obj)
        if len(chunk) == chunksize:
            yield tuple(chunk)
            chunk = []

def phase_grid(R, vR, vT, z, vz, phi, chunksize=5, mp_chunksize=10, filename='test.hdf5', pattern_speed=0):
    image = np.zeros(shape=(R.size, vR.size, vT.size, z.size, vz.size, phi.size))

    grid = product(*map(enumerate, (R, vR, vT, z, vz, phi)))
    grid = clump(grid, chunksize=chunksize)

    with Pool(4) as p:
        data = tuple(tqdm(p.imap_unordered(compute_pixel, grid, mp_chunksize)))

    print('done')

    for chunk in data:
        for ind, value in chunk:
            image[ind] = value
    
    with h5py.File(filename, 'w') as f:
        dset = f.create_dataset('image', data=image)
        dset.attrs['R_min'] = np.min(R)
        dset.attrs['R_max'] = np.max(R)
        dset.attrs['vR_min'] = np.min(vR)
        dset.attrs['vR_max'] = np.max(vR)
        dset.attrs['vT_min'] = np.min(vT)
        dset.attrs['vT_max'] = np.max(vT)
        dset.attrs['z_min'] = np.min(z)
        dset.attrs['z_max'] = np.max(z)
        dset.attrs['vz_min'] = np.min(vz)
        dset.attrs['vz_max'] = np.max(vz)
        dset.attrs['phi_min'] = np.min(phi)
        dset.attrs['phi_max'] = np.max(phi)
    
    print('saved')


if __name__ == '__main__':
    phase_grid(R=R, vR=vR, vT=vT, z=z, vz=vz, phi=phi)






# # square image, size of one side in pixels
# SIZE = 100
# # omega parameter values, in kilometers per second per kiloparsec
# OMEGA_MIN = 0  # km/s/kpc
# OMEGA_MAX = 40  # km/s/kpc
# FRAMES = 41

# # range of R (cylindrical coordinates), in kiloparsecs
# R_MIN = 0  # kpc
# R_MAX = 8  # kpc
# # range of tangential velocity, in kilometers per second
# VT_MIN = 0  # km/s
# VT_MAX = 400  # km/s
# # integration parameters, in gigayears
# STEPSIZE = 0.001  # Gyr
# STEPS = 1500

# # name
# NAME = 'MORE_MW_BAR'
# # save location
# FILENAME = f'{NAME}_over_OMEGA_{OMEGA_MIN}-{OMEGA_MAX}__R_{R_MIN}-{R_MAX}__VT_{VT_MIN}-{VT_MAX}__INT_{STEPSIZE}_{STEPS}.npy'

# # multiprocessing chunking size
# CHUNKSIZE = 100

# # ----------------------------------------------------

# # helpful variables
# X_RES = Y_RES = SIZE
# SHAPE = (FRAMES, X_RES, Y_RES)
# X_RANGE = (R_MIN, R_MAX)
# Y_RANGE = (VT_MIN, VT_MAX)
# EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
# ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)


# # data arrays
# # exclude the first point in X and Y, to avoid 0
# OMEGA_ARR = np.linspace(OMEGA_MIN, OMEGA_MAX, FRAMES)  * u.km/u.s/u.kpc
# T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr
# X_ARR = np.linspace(R_MIN, R_MAX, X_RES + 1)[1:]  * u.kpc
# Y_ARR = np.linspace(VT_MIN, VT_MAX, Y_RES + 1)[1:]  * u.km/u.s

# # potentials
# halo = potential.NFWPotential(conc=10, mvir=1)
# disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
# rotpot_factory = lambda omega: [
#     halo,
#     disc,
#     potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
#     potential.NonInertialFrameForce(Omega = omega)
# ]
# potentials = [rotpot_factory(omega) for omega in OMEGA_ARR]
# def compute_pixel(arg):
#     frame, pot, i, r, j, v = arg
#     initial_condition = [
#         r, 
#         0 * u.km / u.s, 
#         v, 
#         0 * u.kpc, 
#         0 * u.km / u.s, 
#         0 * u.deg
#     ]
#     o = orbit.Orbit(initial_condition)
#     o.integrate(T_ARR, pot, method='dopr54_c')

#     tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
#     return frame, i, j, tess.area


# def main():
#     cube = np.zeros(SHAPE)
#     pixels = [(frame, pot, i, x, j, y) for frame, pot in enumerate(potentials) for i, x in enumerate(X_ARR) for j, y in enumerate(Y_ARR)]
#     with Pool() as p:
#         image_data = [(frame, i, j, value) for frame, i, j, value in tqdm(p.imap_unordered(compute_pixel, pixels, CHUNKSIZE), total=cube.size)]

#     # construct image
#     for frame, i, j, value in image_data:
#         cube[frame, i, j] = value

#     np.save(FILENAME, cube)

#     fig, ax = plt.subplots(figsize = (10, 10))
#     ax.imshow(cube[0].T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
#     plt.show()

# if __name__ == '__main__':
#     main()