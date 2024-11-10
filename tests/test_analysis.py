import pytest
from astropy import coordinates as c
from astropy import units as u
from pidgey.base import Backend

from commensurability import TessellationAnalysis, TessellationAnalysis2D


@pytest.fixture
def dummy_backend():
    class DummyBackend(Backend):
        def ORBIT_TYPE(self):
            return list

        def _compute_orbit(self, skycoord, pot, dt, steps, pattern_speed):
            return c.SkyCoord(
                x=[[0], [0], [0], [1]],
                y=[[0], [0], [1], [0]],
                z=[[0], [1], [0], [0]],
                unit='kpc',
                representation_type='cartesian'
            )

        def _extract_points(self, orbit, pattern_speed):
            return orbit.data.T

    return DummyBackend()


@pytest.fixture
def ic_params():
    ic_function = lambda x, y: c.SkyCoord(
        x=x * u.kpc, y=y * u.kpc, z=0 * u.kpc,
        v_x=0 * u.km/u.s, v_y=0 * u.km/u.s, v_z=0 * u.km/u.s,
        representation_type='cartesian'
    )
    return ic_function, {"x": [0, 1, 2], "y": [0, 1, 2]}


@pytest.fixture
def dummy_potential_func():
    def dummy_potential():
        return 0.0
    return dummy_potential


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
    
    def test_negative_pidgey_chunksize(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, 1, 1, backend=dummy_backend, pidgey_chunksize=-1
            )
    
    def test_negative_mp_chunksize(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, 1, 1, backend=dummy_backend, mp_chunksize=-1
            )

    def test_large_mp_chunksize(self, ic_params, dummy_potential_func, dummy_backend):
        ic_function, ic_values = ic_params
        with pytest.raises(ValueError):
            TessellationAnalysis(
                ic_function, ic_values, dummy_potential_func, 1, 1, backend=dummy_backend, pidgey_chunksize=5, mp_chunksize=1e6
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
        )
        assert analysis.ic_function == ic_function
        assert analysis.ic_values == ic_values
        assert analysis.potential_function == dummy_potential_func
        assert analysis.dt.value == 1
        assert analysis.steps == 1
        assert analysis.backend == dummy_backend

        analysis.save("test_files/test_analysis.hdf5")
        TessellationAnalysis.read_from_hdf5("test_files/test_analysis.hdf5", backend_cls=dummy_backend.__class__)
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
        )
        assert analysis.ic_function == ic_function
        assert analysis.ic_values == ic_values
        assert analysis.potential_function == dummy_potential_func
        assert analysis.dt.value == 1
        assert analysis.steps == 1
        assert analysis.backend == dummy_backend

        analysis.save("test_files/test_analysis.hdf5")
        TessellationAnalysis2D.read_from_hdf5("test_files/test_analysis.hdf5", backend_cls=dummy_backend.__class__)
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
            assert measure == 0.0
