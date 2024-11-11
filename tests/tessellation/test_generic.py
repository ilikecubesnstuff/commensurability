import math

import numpy as np
import pytest

from commensurability.tessellation import Tessellation


class TestNormalizations:
    @pytest.mark.parametrize(
        "norm,ev", [("nsphere_approx", 0), ("convexhull", 1), ("convexhull_rot4", 0)]
    )
    def test_sphere(self, norm, ev):
        points = [
            [1000, 0, 0, 0],
            [1001, 0, 0, 0],
            [1000, 1, 0, 0],
            [1000, 0, 1, 0],
            [1000, 0, 0, 1],
        ]
        tess = Tessellation(
            points,
            normalization_routine=norm,
            axis_ratio=np.inf,
            qhull_options="Qz",
            incremental=False,
        )
        assert math.isclose(tess.measure, ev, abs_tol=1e-6)

    def test_unrecognized_normalization(self):
        points = [
            [1000, 0, 0, 0],
            [1001, 0, 0, 0],
            [1000, 1, 0, 0],
            [1000, 0, 1, 0],
            [1000, 0, 0, 1],
        ]
        with pytest.raises(ValueError, match="Unrecognized normalization routine"):
            Tessellation(
                points,
                normalization_routine="unknown",
                axis_ratio=np.inf,
                qhull_options="Qz",
                incremental=False,
            )
