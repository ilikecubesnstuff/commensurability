import astropy.coordinates as c
import astropy.units as u
import numpy as np

from commensurability import TessellationAnalysis

# rotating bar potential
omega = 30 * u.km / u.s / u.kpc


def pot():
    import galpy.potential as gp

    omega = 30 * u.km / u.s / u.kpc
    halo = gp.NFWPotential(conc=10, mvir=1)
    disc = gp.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
    bar = gp.SoftenedNeedleBarPotential(
        amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega
    )
    pot = [halo, disc, bar]
    return pot


SIZE = 5
FRAMES = 5
values = dict(
    x=np.linspace(0, 10, SIZE + 1)[1:],
    vy=np.linspace(0, 300, SIZE + 1)[1:],
    z=np.linspace(0, 10, FRAMES + 1)[1:],
)


def ic_function(x, vy, z):
    return c.SkyCoord(
        x=x * u.kpc,
        y=0 * u.kpc,
        z=z * u.kpc,
        v_x=0 * u.km / u.s,
        v_y=vy * u.km / u.s,
        v_z=0 * u.km / u.s,
        frame="galactocentric",
        representation_type="cartesian",
    )

if __name__ == "__main__":

    dt = 0.01 * u.Gyr
    steps = 500
    tanal = TessellationAnalysis(
        ic_function, values, pot, dt, steps, pattern_speed=omega, pidgey_chunksize=50
    )
    tanal.launch_interactive_plot("x", "vy")

    tanal.save(f"bar_{SIZE}_{FRAMES}.hdf5")
    tanal.launch_interactive_plot("x", "vy")
