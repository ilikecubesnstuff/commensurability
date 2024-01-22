import astropy.units as u
import gala.dynamics as gd
import gala.potential as gp
import numpy as np
from tessellation import Tessellation

mw = gp.MilkyWayPotential()

w0 = gd.PhaseSpacePosition(
    pos=8 * np.random.random(3) * u.kpc, vel=200 * np.random.random(3) * u.km / u.s
)
t = np.linspace(0, 2, 501) * u.Gyr
orbit = mw.integrate_orbit(w0, t=t)

tess = Tessellation(orbit, ("x", "y", "z"))
print(tess.volume)
tess.plot(plot_included=False, plot_points=True)
tess.plot(plot_included=True, plot_removed=True, plot_points=False)
