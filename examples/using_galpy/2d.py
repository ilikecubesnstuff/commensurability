import numpy as np
import astropy.units as u

import galpy.potential as gp

from commensurability.analysis.coordinates_old import CoordinateCollection
from commensurability.analysis.backends import GalpyBackend
from commensurability.analysis import TessellationAnalysis


class Cylindrical2D(CoordinateCollection):
    R: u.kpc
    vR: u.km / u.s
    vT: u.km / u.s
    phi: u.deg


class Galpy2D(GalpyBackend):

    @staticmethod
    def format_coordinate(coord):
        return [
            coord.R,
            coord.vR,
            coord.vT,
            coord.phi
        ]

    def _extract_points_from_orbit(self, orbit, *, t: u.Quantity, phi_offset: u.Quantity):
        R = orbit.R(t)
        phi = orbit.phi(t) + phi_offset

        x = R * np.cos(phi.value)
        y = R * np.sin(phi.value)

        return np.array([x, y]).T


# rotating bar potential
omega = 30 * u.km/u.s/u.kpc
halo = gp.NFWPotential(conc=10, mvir=1)
disc = gp.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
bar = gp.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega)
pot = [halo, disc, bar]


SIZE = 1
coords = Cylindrical2D(
    R   = np.linspace(0, 10, SIZE + 1)[1:]  * u.kpc,
    vR  = np.linspace(0, 0, 1)  * u.km/u.s,
    vT  = np.linspace(0, 300, SIZE + 1)[1:]  * u.km/u.s,
    phi = np.linspace(0, 0, 1)  * u.deg,
)
dt = 0.01 * u.Gyr
steps = 500
tanal = TessellationAnalysis(pot, dt, steps, pattern_speed=omega, backend=Galpy2D())
tanal.construct_image(coords, chunksize=100)
tanal.launch_interactive_plot()
