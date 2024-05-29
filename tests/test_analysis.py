import numpy as np
import pytest
from pidgey.base import Backend

from commensurability import TessellationAnalysis, TessellationAnalysis2D


@pytest.fixture
def dummy_backend():
    class DummyBackend(Backend):
        def ORBIT_TYPE(self):
            return list

        def _compute_orbit(self, skycoord, pot, dt, steps, pattern_speed):
            return [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]

        def _extract_points(self, orbit, pattern_speed):
            return [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]

    return DummyBackend()


@pytest.fixture
def ic_params():
    return lambda x, y: (x, y), {"x": [0, 1, 2], "y": [0, 1, 2]}


@pytest.fixture
def dummy_potential_func():
    return lambda: None


class TestAnalysis:
    @pytest.fixture
    def analysis(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        return TessellationAnalysis(
            ic_function,
            ic_values,
            dummy_potential_func,
            1,
            1,
            backend=dummy_backend,
            _blank_measures=True,
        )

    def test_invalid_ic_params(self, dummy_potential_func, dummy_backend):
        with pytest.raises(TypeError):
            TessellationAnalysis(None, None, dummy_potential_func, 1, 1, backend=dummy_backend)

    def test_invalid_ic_values(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(ic_function, {}, dummy_potential_func, 1, 1, backend=dummy_backend)

    def test_invalid_potential_func(self, ic_params, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(TypeError):
            TessellationAnalysis(ic_function, ic_values, None, 1, 1, backend=dummy_backend)

    @pytest.mark.parametrize("dt", [0, -1])
    def test_invalid_dt(self, ic_params, dummy_potential_func, dummy_backend, dt):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, dt, 1, backend=dummy_backend
            )

    @pytest.mark.parametrize("steps", [0, -1])
    def test_invalid_steps(self, ic_params, dummy_potential_func, dummy_backend, steps):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, 1, steps, backend=dummy_backend
            )

    def test_unrecognized_backend(self, ic_params, dummy_potential_func):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, 1, 1, backend="unknown"
            )

    def test_analysis_init(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        analysis = TessellationAnalysis(
            ic_function,
            ic_values,
            dummy_potential_func,
            1,
            1,
            backend=dummy_backend,
            _blank_measures=True,
        )
        assert analysis.ic_function == ic_function
        assert analysis.ic_values == ic_values
        assert analysis.potential_function == dummy_potential_func
        assert analysis.dt.value == 1
        assert analysis.steps == 1
        assert analysis.backend == dummy_backend

    def test_analysis_measures(self, analysis):
        for pixel in analysis:
            ic, measure = analysis[pixel]
            # specifically for these dummy examples
            assert ic == pixel
            assert measure == 0.0


class TestAnalysis2D:
    @pytest.fixture
    def analysis_2d(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        return TessellationAnalysis2D(
            ic_function,
            ic_values,
            dummy_potential_func,
            1,
            1,
            backend=dummy_backend,
            _blank_measures=True,
        )

    def test_invalid_ic_params(self, dummy_potential_func, dummy_backend):
        with pytest.raises(TypeError):
            TessellationAnalysis2D(None, None, dummy_potential_func, 1, 1, backend=dummy_backend)

    def test_invalid_ic_values(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis2D(
                ic_function, {}, dummy_potential_func, 1, 1, backend=dummy_backend
            )

    def test_invalid_potential_func(self, ic_params, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(TypeError):
            TessellationAnalysis2D(ic_function, ic_values, None, 1, 1, backend=dummy_backend)

    @pytest.mark.parametrize("dt", [0, -1])
    def test_invalid_dt(self, ic_params, dummy_potential_func, dummy_backend, dt):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis2D(
                ic_function, ic_values, dummy_potential_func, dt, 1, backend=dummy_backend
            )

    @pytest.mark.parametrize("steps", [0, -1])
    def test_invalid_steps(self, ic_params, dummy_potential_func, dummy_backend, steps):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis2D(
                ic_function, ic_values, dummy_potential_func, 1, steps, backend=dummy_backend
            )

    def test_unrecognized_backend(self, ic_params, dummy_potential_func):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis2D(
                ic_function, ic_values, dummy_potential_func, 1, 1, backend="unknown"
            )

    def test_analysis_init(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        analysis = TessellationAnalysis2D(
            ic_function,
            ic_values,
            dummy_potential_func,
            1,
            1,
            backend=dummy_backend,
            _blank_measures=True,
        )
        assert analysis.ic_function == ic_function
        assert analysis.ic_values == ic_values
        assert analysis.potential_function == dummy_potential_func
        assert analysis.dt.value == 1
        assert analysis.steps == 1
        assert analysis.backend == dummy_backend

    def test_analysis_measures(self, analysis_2d):
        for pixel in analysis_2d:
            ic, measure = analysis_2d[pixel]
            # specifically for these dummy examples
            assert ic == pixel
            assert measure == 0.0
