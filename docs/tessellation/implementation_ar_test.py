from pathlib import Path

import astropy.coordinates as c
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np
import pytest

from commensurability import TessellationAnalysis as _TessellationAnalysis
from commensurability.tessellation import Tessellation

AGAMA_AVAILABLE = False
try:
    import agama

    AGAMA_AVAILABLE = True
except ImportError:
    pass


class AR0(_TessellationAnalysis):
    ar = 0

    @staticmethod
    def evaluate(orbit):
        return Tessellation(orbit, incremental=False, axis_ratio=0)

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        return Tessellation(orbit, incremental=False, axis_ratio=0).measure


class AR5(_TessellationAnalysis):
    ar = 5

    @staticmethod
    def evaluate(orbit):
        return Tessellation(orbit, incremental=False, axis_ratio=5)

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        return Tessellation(orbit, incremental=False, axis_ratio=5).measure


class AR10(_TessellationAnalysis):
    ar = 10

    @staticmethod
    def evaluate(orbit):
        return Tessellation(orbit, incremental=False, axis_ratio=10)

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        return Tessellation(orbit, incremental=False, axis_ratio=10).measure


class AR15(_TessellationAnalysis):
    ar = 15

    @staticmethod
    def evaluate(orbit):
        return Tessellation(orbit, incremental=False, axis_ratio=15)

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        return Tessellation(orbit, incremental=False, axis_ratio=15).measure


class AR20(_TessellationAnalysis):
    ar = 20

    @staticmethod
    def evaluate(orbit):
        return Tessellation(orbit, incremental=False, axis_ratio=20)

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        return Tessellation(orbit, incremental=False, axis_ratio=20).measure


@pytest.mark.skipif(not AGAMA_AVAILABLE, reason="Agama is not available")
@pytest.mark.parametrize("cls", [AR0, AR5, AR10, AR15, AR20])
def test_axis_ratio_images(cls):
    folder = Path(__file__).parent
    tanal = cls.read_from_hdf5(folder / f"ar{cls.ar}.hdf5")

    def potential_definition():
        import agama

        potential = agama.Potential(
            dict(type="MiyamotoNagai", mass=3e10, scaleRadius=5, scaleHeight=0.5),
            dict(
                type="Dehnen", mass=8e10, scaleRadius=4, gamma=0.7, axisRatioY=0.8, axisRatioZ=0.5
            ),
        )
        return potential

    def initial_condition(x, vy):
        return c.SkyCoord(
            x=x * u.kpc,
            y=0 * u.kpc,
            z=1 * u.kpc,
            v_x=0 * u.km / u.s,
            v_y=vy * u.km / u.s,
            v_z=0 * u.km / u.s,
            frame="galactocentric",
            representation_type="cartesian",
        )

    # define the ranges of input for initial_condition
    N = 100
    values = dict(
        x=np.linspace(0, 15, N + 1)[1:],
        vy=np.linspace(0, 250, N + 1)[1:],
    )

    dt = 0.01 * u.Gyr
    steps = 500
    omega = 30 * u.km / u.s / u.kpc

    new_tanal = cls(
        initial_condition,
        values,
        potential_definition,
        dt,
        steps,
        pattern_speed=omega,
        pidgey_chunksize=500,
        mp_chunksize=10,
    )
    assert np.allclose(tanal.measures, new_tanal.measures)
