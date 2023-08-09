
import numpy as np
import astropy.units as u

import gala.potential as gp
import gala.dynamics as gd

from commensurability.tessellation import Tessellation


mw = gp.MilkyWayPotential()

w0 = gd.PhaseSpacePosition(
    pos=8 * np.random.random(3) * u.kpc,
    vel=200 * np.random.random(3) * u.km/u.s
)
t = np.linspace(0, 2, 501) * u.Gyr
orbit = mw.integrate_orbit(w0, t=t)

tess = Tessellation.from_gala_orbit(orbit)
print(tess.volume)
tess.plot_tessellation_trimming(plot_included=False, plot_points=True)
tess.plot_tessellation_trimming(plot_included=True, plot_points=False)