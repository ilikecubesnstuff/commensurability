

import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt

from commensurability.analysis.coordinates import Cylindrical
from commensurability.analysis.analysis import TessellationAnalysis


def potential():
    import galpy.potential as p
    omega = 30 * u.km/u.s/u.kpc
    halo = p.NFWPotential(conc=10, mvir=1)
    disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
    bar = p.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
    pot = [halo, disc, bar]
    return pot


SIZE = 30
FRAMES = 1

RMIN = 0
RMAX = 10
VMIN = 0
VMAX = 300

coords = Cylindrical(
    R   = np.linspace(RMIN, RMAX, SIZE + 1)[1:]  * u.kpc,
    vR  = np.linspace(0, 0, 1)  * u.km/u.s,
    vT  = np.linspace(VMIN, VMAX, SIZE + 1)[1:]  * u.km/u.s,
    z   = np.linspace(1, 1, FRAMES + 1)[1:]  * u.kpc,
    vz  = np.linspace(0, 0, 1)  * u.km/u.s,
    phi = np.linspace(0, 0, 1)  * u.deg,
)
dt = 0.01 * u.Gyr
steps = 500
canal = TessellationAnalysis(potential, dt, steps, pattern_speed=30 * u.km/u.s/u.kpc)
img = canal.construct_image(coords, chunksize=10)

np.save('image.npy', img)

plt.imshow(img.T, origin='lower', extent=(RMIN, RMAX, VMIN, VMAX), aspect=(RMAX-RMIN)/(VMAX-VMIN))
plt.show()

# canal.save_image(f'mw_bar_{SIZE}_{FRAMES}.hdf5')
# canal.launch_interactive_plot()