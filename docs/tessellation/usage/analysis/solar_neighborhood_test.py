from pathlib import Path

import astropy.coordinates as c
import astropy.units as u
import numpy as np
import pytest

from commensurability import TessellationAnalysis

GALPY_AVAILABLE = False
try:
    import galpy

    GALPY_AVAILABLE = True

except ImportError:
    pass


folder = Path(__file__).parent
tanal = (
    TessellationAnalysis.read_from_hdf5(folder / "solar_neighborhood.hdf5")
    if GALPY_AVAILABLE
    else None
)


@pytest.mark.skipif(not GALPY_AVAILABLE, reason="Galpy not available")
def test_hdf_output():
    def potential_definition():
        from galpy.potential.mwpotentials import Irrgang13I as potential

        return potential

    def initial_condition(x, vy, z):
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

    values = dict(
        x=np.linspace(6, 10, 40),
        vy=np.linspace(150, 300, 40),
        z=np.linspace(0, 2, 20),
    )

    dt = 0.01 * u.Gyr
    steps = 500
    omega = 50 * u.km / u.s / u.kpc

    new_tanal = TessellationAnalysis(
        initial_condition,
        values,
        potential_definition,
        dt,
        steps,
        pattern_speed=omega,
        pidgey_chunksize=500,
        mp_chunksize=20,
    )
    assert np.isclose(new_tanal.measures, tanal.measures).all()
