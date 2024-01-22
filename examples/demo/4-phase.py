import astropy.coordinates as c
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

# package imports
from commensurability import TessellationAnalysis

# galpy imports moved inside the potential function


# defining the potential
def potential_function():
    import galpy.potential as p

    omega = 30 * u.km / u.s / u.kpc
    halo = p.NFWPotential(conc=10, mvir=1)
    disc = p.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
    bar = p.SoftenedNeedleBarPotential(
        amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega
    )
    pot = [halo, disc, bar]
    return pot


# integrating the orbits over a grid
SIZE = 20
values = dict(
    X=np.linspace(0, 6, SIZE + 1)[1:],
    vY=np.linspace(100, 250, SIZE + 1)[1:],
)


def ic_function(X, vY):
    return c.SkyCoord(
        x=X * u.kpc,
        y=0 * u.kpc,
        z=1 * u.kpc,
        v_x=0 * u.km / u.s,
        v_y=vY * u.km / u.s,
        v_z=0 * u.km / u.s,
        frame="galactocentric",
        representation_type="cartesian",
    )


dt = 0.01 * u.Gyr
steps = 500
tanal = TessellationAnalysis(
    ic_function, values, potential_function, dt, steps, pattern_speed=30 * u.km / u.s / u.kpc
)

# save to hdf5 file
tanal.save("demo.hdf5")

# generate plot
img = tanal.image.T
plt.imshow(img, origin="lower", extent=(0, 6, 100, 250), aspect=6 / 150)
plt.show()
