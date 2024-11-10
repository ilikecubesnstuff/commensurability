import math

import astropy.coordinates as c
import astropy.units as u
import numpy as np
import pytest

from commensurability.tessellation import Tessellation

class TestTessellationConstructor:
    
    def test_list_subclass(self):
        
        class other_list(list):
            pass
        
        points = other_list([
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1],
        ])
        tess = Tessellation(points, axis_ratio=np.inf, qhull_options="Qz", incremental=False)
        assert math.isclose(tess.measure, 1)

    def test_bad_dims_for_orbit(self):
        points = np.random.random((10, 3))
        with pytest.raises(ValueError):
            tess = Tessellation(points, dims_for_orbit=[0, 1, 2])

    def test_cartersian_representation(self):
        points = c.CartesianRepresentation(
            x = [1, -1, 0, 0, 0, 0] * u.kpc,
            y = [0, 0, 1, -1, 0, 0] * u.kpc,
            z = [0, 0, 0, 0, 1, -1] * u.kpc,
        )
        tess = Tessellation(points, axis_ratio=np.inf, qhull_options="Qz", incremental=False)
        assert math.isclose(tess.measure, 1)
