import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt

# galpy imports

# galpy imports moved inside the potential function

# package imports
from commensurability.analysis.coordinates import Cylindrical
from commensurability.analysis.analysis import TessellationAnalysis

# defining the potential
def potential_function():
    import galpy.potential as p
    omega = 30 * u.km/u.s/u.kpc
    halo = p.NFWPotential(conc=10, mvir=1)
    disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
    bar = p.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
    pot = [halo, disc, bar]
    return pot

# integrating the orbits over a grid
SIZE = 20
coords = Cylindrical(
    R = np.linspace(0, 6, SIZE + 1)[1:] * u.kpc,
    vR  = 0 * u.km/u.s,
    vT  = np.linspace(100, 250, SIZE + 1)[1:] * u.km/u.s,
    z   = 1 * u.kpc,
    vz  = 0 * u.km/u.s,
    phi = 0 * u.deg,
)
dt = 0.004 * u.Gyr
steps = 500
canal = TessellationAnalysis(potential_function, dt, steps, pattern_speed=30 * u.km/u.s/u.kpc)
img = canal.construct_image(coords, chunksize=10)

# save to hdf5 file
from commensurability.analysis.fileio import FileIO
f = FileIO('demo.hdf5')
f.save(canal)

# generate plot
plt.imshow(img.T, origin='lower', extent=(0, 6, 100, 250), aspect=6/150)
plt.show()
