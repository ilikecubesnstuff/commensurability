import astropy.coordinates as c
import astropy.units as u
import numpy as np

from commensurability import TessellationAnalysis

# rotating bar potential
omega = 30 * u.km / u.s / u.kpc


def pot():
    import gala.potential as gp
    from gala.units import galactic

    disk = gp.MiyamotoNagaiPotential(m=6e10 * u.Msun, a=3.5 * u.kpc, b=280 * u.pc, units=galactic)
    halo = gp.NFWPotential(m=6e11 * u.Msun, r_s=20.0 * u.kpc, units=galactic)
    bar = gp.LongMuraliBarPotential(
        m=1e10 * u.Msun,
        a=4 * u.kpc,
        b=0.8 * u.kpc,
        c=0.25 * u.kpc,
        alpha=25 * u.degree,
        units=galactic,
    )
    pot = gp.CCompositePotential()
    pot["disk"] = disk
    pot["halo"] = halo
    pot["bar"] = bar

    frame = gp.ConstantRotatingFrame(Omega=[0, 0, 30] * u.km / u.s / u.kpc, units=galactic)
    ham = gp.Hamiltonian(pot, frame=frame)
    return ham


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

    tanal = TessellationAnalysis(
        ic_function, values, pot, dt, steps, pattern_speed=omega, pidgey_chunksize=50
    )
    tanal.launch_interactive_plot("x", "vy")

    tanal.save(f"examples/using_galpy/bar_{SIZE}_{FRAMES}.hdf5")
    tanal.launch_interactive_plot("x", "vy")
