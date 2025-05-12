from pathlib import Path

import astropy.coordinates as c
import astropy.units as u
import numpy as np
import pytest

from commensurability import TessellationAnalysis2D

AGAMA_AVAILABLE = False
try:
    import agama

    AGAMA_AVAILABLE = True
except ImportError:
    pass


def potential_definition_no_bar():
    import agama

    nfw_pot = dict(type="NFW", mass=1e12, scaleRadius=20)
    potential = agama.Potential(nfw_pot)
    return potential


def potential_definition_bar():
    import agama

    bar_pot = dict(
        type="Ferrers",
        mass=1e9,
        scaleRadius=3.0,
        axisRatioY=0.5,
        axisratioz=0.4,
    )
    nfw_pot = dict(type="NFW", mass=1e12, scaleRadius=20)
    potential = agama.Potential(nfw_pot, bar_pot)
    return potential


def potential_definition_big_bar():
    import agama

    bar_pot = dict(
        type="Ferrers",
        mass=1e10,
        scaleRadius=3.0,
        axisRatioY=0.5,
        axisratioz=0.4,
    )

    nfw_pot = dict(type="NFW", mass=1e12, scaleRadius=20)
    potential = agama.Potential(nfw_pot, bar_pot)
    return potential


folder = Path(__file__).parent
tanal_no_bar = (
    TessellationAnalysis2D.read_from_hdf5(folder / "rotating_bar_no_bar.hdf5")
    if AGAMA_AVAILABLE
    else None
)
tanal_bar = (
    TessellationAnalysis2D.read_from_hdf5(folder / "rotating_bar_bar.hdf5")
    if AGAMA_AVAILABLE
    else None
)
tanal_big_bar = (
    TessellationAnalysis2D.read_from_hdf5(folder / "rotating_bar_big_bar.hdf5")
    if AGAMA_AVAILABLE
    else None
)


@pytest.mark.skipif(not AGAMA_AVAILABLE, reason="Agama not available")
@pytest.mark.parametrize(
    ["pot", "tanal"],
    [
        (potential_definition_no_bar, tanal_no_bar),
        (potential_definition_bar, tanal_bar),
        (potential_definition_big_bar, tanal_big_bar),
    ],
)
def test_hdf_output(pot, tanal):
    def initial_condition(x, vy):
        return c.SkyCoord(
            x=x * u.kpc,
            y=0 * u.kpc,
            z=0 * u.kpc,
            v_x=0 * u.km / u.s,
            v_y=vy * u.km / u.s,
            v_z=0 * u.km / u.s,
            frame="galactocentric",
            representation_type="cartesian",
        )

    # define the ranges of input for initial_condition
    values = dict(
        x=np.linspace(0.1, 8, 100),
        vy=np.linspace(20, 400, 100),
    )

    dt = 0.01 * u.Gyr
    steps = 500
    omega = 30 * u.km / u.s / u.kpc

    new_tanal = TessellationAnalysis2D(
        initial_condition,
        values,
        pot,
        dt,
        steps,
        pattern_speed=omega,
        pidgey_chunksize=500,
        mp_chunksize=20,
    )
    assert np.isclose(new_tanal.measures, tanal.measures).all()
