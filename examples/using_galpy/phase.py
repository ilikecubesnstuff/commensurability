import numpy as np
import astropy.units as u
import galpy.potential as p

from commensurability.analysis import TessellationAnalysis
from commensurability.analysis.coordinates import Cylindrical

# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = p.NFWPotential(conc=10, mvir=1)
disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = p.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]


SIZE = 50
FRAMES = 20
coords = Cylindrical(
    R   = np.linspace(0, 10, SIZE + 1)[1:]  * u.kpc,
    vR  = np.linspace(0, 0, 1)  * u.km/u.s,
    vT  = np.linspace(0, 300, SIZE + 1)[1:]  * u.km/u.s,
    z   = np.linspace(0, 2, FRAMES + 1)[1:]  * u.kpc,
    vz  = np.linspace(0, 0, 1)  * u.km/u.s,
    phi = np.linspace(0, 0, 1)  * u.deg,
)
dt = 0.01 * u.Gyr
steps = 500
canal = TessellationAnalysis(pot, dt, steps, pattern_speed=omega)
canal.construct_image(coords, chunksize=1)

canal.pot_string = """
import astropy.units as u
import galpy.potential as p
omega = 30 * u.km/u.s/u.kpc
halo = p.NFWPotential(conc=10, mvir=1)
disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = p.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]
"""
canal.save_image(f'mw_bar_{SIZE}_{FRAMES}.hdf5')
canal.launch_interactive_plot()