import numpy as np
import pytest

from commensurability.viewer import Viewer


class TestViewerInit:
    def test_empty_image(self):
        with pytest.raises(ValueError):
            Viewer(np.array([]), {})

    def test_1d_image(self):
        with pytest.raises(ValueError):
            Viewer(np.array([1, 2, 3, 4, 5]), {})

    @pytest.mark.parametrize(
        "nd_image,axlims",
        (
            (np.arange(15).reshape((3, 5)), {"a": [0, 2], "b": [0, 4], "c": [0, 2]}),
            (np.arange(15).reshape((3, 5)), {"a": [0, 2]}),
        ),
    )
    def test_invalid_axes(self, nd_image, axlims):
        with pytest.raises(ValueError):
            Viewer(nd_image, axlims)

    @pytest.mark.parametrize(
        "nd_image,axlims",
        (
            (np.arange(15).reshape((3, 5)), {"a": [0, 2], "b": [0, 1, 2, 3]}),
            (np.arange(15).reshape((3, 5)), {"a": [0, 2], "b": []}),
        ),
    )
    def test_invalid_axis_lengths(self, nd_image, axlims):
        with pytest.raises(ValueError):
            Viewer(nd_image, axlims)

    def test_2d_image(self):
        nd_image = np.arange(6).reshape((2, 3))
        axlims = {
            "a": [0, 1],
            "b": [0, 2],
        }
        v = Viewer(nd_image, axlims)
        assert np.all(v.im == nd_image)
        assert v.shape == nd_image.shape
        assert v.axnames[0] == "a"
        assert v.axnames[1] == "b"
        assert all(a == b for a, b in zip(v.axvalues[0], [0, 1]))
        assert all(a == b for a, b in zip(v.axvalues[1], [0, 1, 2]))
        assert v.axsteps[0] == 1
        assert v.axsteps[1] == 1
        assert v.ihax == 0
        assert v.ivax == 1
        assert v.isax is None

    def test_3d_image(self):
        nd_image = np.arange(24).reshape((2, 3, 4))
        axlims = {
            "a": [0, 1],
            "b": [0, 2],
            "c": [0, 3],
        }
        v = Viewer(nd_image, axlims)
        assert np.all(v.im == nd_image)
        assert v.shape == nd_image.shape
        assert v.axnames[0] == "a"
        assert v.axnames[1] == "b"
        assert v.axnames[2] == "c"
        assert all(a == b for a, b in zip(v.axvalues[0], [0, 1]))
        assert all(a == b for a, b in zip(v.axvalues[1], [0, 1, 2]))
        assert all(a == b for a, b in zip(v.axvalues[2], [0, 1, 2, 3]))
        assert v.axsteps[0] == 1
        assert v.axsteps[1] == 1
        assert v.axsteps[1] == 1
        assert v.ihax == 0
        assert v.ivax == 1
        assert v.isax == 2

    @pytest.mark.parametrize(
        "x_axis,y_axis,s_axis",
        (
            (0, None, None),
            (None, 1, None),
            (None, None, 2),
            (0, 1, None),
            (0, None, 2),
            (None, 1, 2),
        ),
    )
    def test_incorrect_axis_args(self, x_axis, y_axis, s_axis):
        nd_image = np.arange(24).reshape((2, 3, 4))
        axlims = {
            "a": [0, 1],
            "b": [0, 2],
            "c": [0, 3],
        }
        with pytest.raises(ValueError):
            Viewer(nd_image, axlims, x_axis=x_axis, y_axis=y_axis, s_axis=s_axis)

    def test_repeated_axes(self):
        nd_image = np.arange(24).reshape((2, 3, 4))
        axlims = {
            "a": [0, 1],
            "b": [0, 2],
            "c": [0, 3],
        }
        with pytest.raises(ValueError):
            Viewer(nd_image, axlims, x_axis=0, y_axis=0, s_axis=0)
