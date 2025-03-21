import astropy.coordinates as c
import astropy.units as u
import numpy as np

from commensurability import TessellationAnalysis

# rotating bar potential
omega = 30 * u.km / u.s / u.kpc


def pot():
    import agama

    bar_par = dict(
        type="Ferrers",
        mass=1e9,
        scaleRadius=1.0,
        axisRatioY=0.5,
        axisratioz=0.4,
    )
    disk_par = dict(type="Disk", mass=5e10, scaleRadius=3, scaleHeight=0.4)
    bulge_par = dict(type="Sersic", mass=1e10, scaleRadius=1, axisRatioZ=0.6)
    halo_par = dict(type="NFW", mass=1e12, scaleRadius=20)
    potgal = agama.Potential(disk_par, bulge_par, halo_par, bar_par)
    return potgal


SIZE = 20
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
    from pathlib import Path

    dt = 0.01 * u.Gyr
    steps = 500
    tanal = TessellationAnalysis(ic_function, values, pot, dt, steps, pattern_speed=omega)
    tanal.launch_interactive_plot("x", "vy")

    tanal.save(Path(__file__).parent / f"bar_{SIZE}_{FRAMES}.hdf5")
    tanal.launch_interactive_plot("x", "vy")
