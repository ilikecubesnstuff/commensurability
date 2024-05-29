import math

import numpy as np
import pytest

from commensurability.tessellation import Tessellation
from commensurability.tessellation.exceptions import LowDimensionalityException

rng = np.random.default_rng(0)


class TestInsufficientDimensionality:
    @pytest.mark.parametrize(
        "points",
        [
            True,
            False,
            0,
            1,
            -1,
            0.0,
            1.5,
            1.482e-100,
        ],
    )
    def test_zero_dimensional_numeric_builtins(self, points):
        arr = np.array(points)
        assert arr.size == 1
        assert arr.ndim == 0
        assert arr.shape == ()
        with pytest.raises(ValueError):
            Tessellation(points)
        with pytest.raises(ValueError):
            Tessellation(arr)

    @pytest.mark.parametrize(
        "points",
        [
            {},
            {"a": 1},
            {"a": 1, "b": 2},
            set(),
            {0},
            {0, 1},
            {0, 1, 2, 3},
        ],
    )
    def test_zero_dimensional_container_builtins(self, points):
        arr = np.array(points)
        assert arr.size == 1
        assert arr.ndim == 0
        assert arr.shape == ()
        with pytest.raises(TypeError):
            Tessellation(points)
        with pytest.raises(TypeError):
            Tessellation(arr)

    @pytest.mark.filterwarnings("ignore:Casting complex values")
    @pytest.mark.parametrize(
        "points,exc1,exc2",
        [
            (1j, TypeError, ValueError),
            ("", ValueError, ValueError),
            ("a", ValueError, ValueError),
            ("asdf", ValueError, ValueError),
        ],
    )
    def test_zero_dimensional_noncasting_builtins(self, points, exc1, exc2):
        arr = np.array(points)
        assert arr.size == 1
        assert arr.ndim == 0
        assert arr.shape == ()
        with pytest.raises(exc1):
            Tessellation(points)
        with pytest.raises(exc2):
            Tessellation(arr)

    @pytest.mark.parametrize(
        "points",
        [
            [],
            [0],
            [0, 1],
            [0, 1, 2],
            [0, 1, 2, 3],
            (),
            (0,),
            (0, 1),
            (0, 1, 2),
            (0, 1, 2, 3),
        ],
    )
    def test_one_dimensional_container_builtins(self, points):
        arr = np.array(points)
        assert arr.ndim == 1
        with pytest.raises(ValueError):
            Tessellation(points)
        with pytest.raises(ValueError):
            Tessellation(arr)

    @pytest.mark.parametrize(
        "points",
        [
            [[], []],
            [[0], [1]],
            ([], []),
            ([0], [1]),
            [(), ()],
            [(0,), (1,)],
            ((), ()),
            ((0,), (1,)),
        ],
    )
    def test_two_dimensional_container_builtins(self, points):
        arr = np.array(points)
        print(points, arr)
        assert arr.ndim == 2
        with pytest.raises(LowDimensionalityException):
            Tessellation(points)
        with pytest.raises(LowDimensionalityException):
            Tessellation(arr)

    @pytest.mark.parametrize(
        "points",
        [
            [[], [0]],
            [[], [], [1], []],
            [[0], [1, 2]],
            [[0, 1], [2]],
        ],
    )
    def test_two_dimensional_container_builtins_inhomogeneity(self, points):
        with pytest.raises(ValueError, match="inhomogeneous"):
            Tessellation(points)

    @pytest.mark.parametrize(
        "points",
        [
            rng.random((0, 0)),
            rng.random((1, 0)),
            rng.random((2, 0)),
            rng.random((0, 1)),
            rng.random((1, 1)),
            rng.random((2, 1)),
        ],
    )
    def test_ndarray(self, points):
        with pytest.raises(LowDimensionalityException):
            Tessellation(points)


class TestDegeneracies:
    @pytest.mark.parametrize(
        "points",
        [
            rng.random((0, 2)),
            rng.random((0, 3)),
            rng.random((0, 4)),
        ],
    )
    def test_empty_point_array(self, points):
        with pytest.raises(ValueError, match="No points given"):
            Tessellation(points)

    @pytest.mark.parametrize(
        "points",
        [
            rng.random((1, 2)),
            rng.random((2, 2)),
            rng.random((3, 2)),
        ],
    )
    def test_insufficient_points_in_two_dimensions(self, points):
        with pytest.warns(UserWarning, match="degenerate"):
            tess = Tessellation(points)
        assert tess.measure == 0.0

    @pytest.mark.parametrize(
        "points",
        [
            rng.random((1, 3)),
            rng.random((2, 3)),
            rng.random((3, 3)),
            rng.random((4, 3)),
        ],
    )
    def test_insufficient_points_in_three_dimensions(self, points):
        with pytest.warns(UserWarning, match="degenerate"):
            tess = Tessellation(points)
        assert tess.measure == 0.0

    # @pytest.mark.parametrize(
    #     "points",
    #     [
    #         rng.random((1, 4)),
    #         rng.random((2, 4)),
    #         rng.random((3, 4)),
    #         rng.random((4, 4)),
    #         rng.random((5, 4)),
    #     ],
    # )
    # def test_insufficient_points_in_four_dimensions(self, points):
    #     with pytest.warns(UserWarning, match="degenerate"):
    #         tess = Tessellation(points)
    #     assert tess.measure == 0.0

    @pytest.mark.parametrize(
        "points",
        [
            np.array(
                [
                    np.zeros(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    np.zeros(100),
                    rng.random(100),
                ]
            ).T,
            np.array(
                [
                    rng.random(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    np.arange(100),
                    np.arange(100),
                ]
            ).T,
            np.array(
                [
                    np.arange(100),
                    np.arange(100) * 2,
                ]
            ).T,
            np.array(
                [
                    (x := rng.random(100)),
                    3 * x - 4,
                ]
            ).T,
        ],
    )
    def test_degeneracy_in_two_dimensions(self, points):
        with pytest.warns(UserWarning, match="degenerate"):
            tess = Tessellation(points)
        assert tess.measure == 0.0

    @pytest.mark.parametrize(
        "points",
        [
            np.array(
                [
                    np.zeros(100),
                    np.zeros(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    rng.random(100),
                    np.zeros(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    np.zeros(100),
                    rng.random(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    np.zeros(100),
                    np.zeros(100),
                    rng.random(100),
                ]
            ).T,
            np.array(
                [
                    rng.random(100),
                    rng.random(100),
                    np.zeros(100),
                ]
            ).T,
            np.array(
                [
                    rng.random(100),
                    np.zeros(100),
                    rng.random(100),
                ]
            ).T,
            np.array(
                [
                    np.zeros(100),
                    rng.random(100),
                    rng.random(100),
                ]
            ).T,
            np.array(
                [
                    np.arange(100),
                    np.arange(100),
                    np.arange(100),
                ]
            ).T,
            np.array(
                [
                    np.arange(100),
                    np.arange(100) * 2,
                    np.arange(100) * 3,
                ]
            ).T,
            np.array(
                [
                    (x := rng.random(100)),
                    5 - 7 * x,
                    4 + 3 * x,
                ]
            ).T,
            np.array(
                [
                    (x := rng.random(100)),
                    (y := rng.random(100)),
                    9 + 4 * x - 3 * y,
                ]
            ).T,
        ],
    )
    def test_degeneracy_in_three_dimensions(self, points):
        with pytest.warns(UserWarning, match="degenerate"):
            tess = Tessellation(points)
        assert tess.measure == 0.0

    # @pytest.mark.parametrize(
    #     "points",
    #     [
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 rng.random(100),
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.zeros(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #                 rng.random(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.arange(100),
    #                 np.arange(100),
    #                 np.arange(100),
    #                 np.arange(100),
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 np.arange(100),
    #                 np.arange(100) * 2,
    #                 np.arange(100) * 3,
    #                 np.arange(100) * 4,
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 (x := rng.random(100)),
    #                 8 * x - 9,
    #                 7 * x + 5,
    #                 2 - 3 * x,
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 (x := rng.random(100)),
    #                 (y := rng.random(100)),
    #                 3 + 4 * x - 6 * y,
    #                 2 - 9 * x - 8 * y,
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 (x := rng.random(100)),
    #                 (y := rng.random(100)),
    #                 3 + 4 * x - 6 * y,
    #                 2 - 9 * x - 8 * y,
    #             ]
    #         ).T,
    #         np.array(
    #             [
    #                 (x := rng.random(100)),
    #                 (y := rng.random(100)),
    #                 (z := rng.random(100)),
    #                 4 * x - 4 * y + 3 * z - 18,
    #             ]
    #         ).T,
    #     ],
    # )
    # def test_degeneracy_in_four_dimensions(self, points):
    #     with pytest.warns(UserWarning, match="degenerate"):
    #         tess = Tessellation(points)
    #     assert tess.measure == 0.0


class TestMeasure:
    @pytest.mark.parametrize("points", rng.normal(-1, 1, (20, 100, 2)))
    def test_normalized_range(self, points):
        for axis_ratio in (0, 5, 10, 15, 20, 50, 100, np.inf):
            tess = Tessellation(points, axis_ratio=axis_ratio)
            assert 0 <= tess.measure <= 1

    @pytest.mark.parametrize(
        "points,expected_measure",
        [
            ([[1, 0], [0, 1], [-1, 0], [0, 0]], 1 / np.pi),
            ([[1, 0], [0, 1], [-1, 0], [0, -1]], 2 / np.pi),
            ([[0, 0], [0, 1], [1, 0], [1, 1]], 1 / (2 * np.pi)),
        ],
    )
    def test_manual_point_sets_in_2D(self, points, expected_measure):
        tess = Tessellation(points, axis_ratio=np.inf, qhull_options="Qz", incremental=False)
        assert math.isclose(tess.measure, expected_measure)

    @pytest.mark.parametrize(
        "points,expected_measure",
        [
            (
                [
                    [1, 0, 0],
                    [-1, 0, 0],
                    [0, 1, 0],
                    [0, -1, 0],
                    [0, 0, 1],
                    [0, 0, -1],
                ],
                1,
            )
        ],
    )
    def test_manual_point_sets_in_3D(self, points, expected_measure):
        tess = Tessellation(points, axis_ratio=np.inf, qhull_options="Qz", incremental=False)
        assert math.isclose(tess.measure, expected_measure)

    # @pytest.mark.parametrize(
    #     "points,expected_measure",
    #     [
    #         (rng.normal(size=(100, 2)), 0.45906549045400247),
    #         (rng.normal(size=(100, 2)), 0.3943940252036827),
    #         (rng.normal(size=(100, 2)), 0.4336073562797213),
    #         (rng.normal(size=(100, 2)), 0.5617838554666587),
    #         (rng.normal(size=(100, 2)), 0.5985426693438319),
    #         (rng.normal(size=(100, 2)), 0.5123637204843497),
    #         (rng.normal(size=(100, 2)), 0.3225978521940026),
    #         (rng.normal(size=(100, 2)), 0.4143084419365352),
    #         (rng.normal(size=(100, 2)), 0.5987423967178952),
    #         (rng.normal(size=(100, 2)), 0.45548485279657114),
    #     ],
    # )
    # def test_pseudorandom_point_sets_in_2D(self, points, expected_measure):
    #     tess = Tessellation(points)
    #     assert tess.measure == expected_measure

    # @pytest.mark.parametrize(
    #     "points,expected_measure",
    #     [
    #         (rng.normal(size=(100, 3)), 0.5919362630015677),
    #         (rng.normal(size=(100, 3)), 0.4964502307751198),
    #         (rng.normal(size=(100, 3)), 0.5315301767521167),
    #         (rng.normal(size=(100, 3)), 0.5627029309700805),
    #         (rng.normal(size=(100, 3)), 0.6854798548331412),
    #         (rng.normal(size=(100, 3)), 0.4686263346093926),
    #         (rng.normal(size=(100, 3)), 0.6370942709595918),
    #         (rng.normal(size=(100, 3)), 0.4930328558372991),
    #         (rng.normal(size=(100, 3)), 0.5546090138460925),
    #         (rng.normal(size=(100, 3)), 0.5457828455144428),
    #     ],
    # )
    # def test_pseudorandom_point_sets_in_3D(self, points, expected_measure):
    #     tess = Tessellation(points)
    #     assert tess.measure == expected_measure
