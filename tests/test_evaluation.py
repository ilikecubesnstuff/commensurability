import astropy.coordinates as c
import astropy.units as u
import pytest

from commensurability.evaluation import Evaluation

class TestEvaluation:

    def test_subclass(self):

        class TestEvaluation(Evaluation):

            @property
            def measure(self):
                return 0.0

            def plot(self):
                pass

        obj = type('obj', (), {})()
        ev = TestEvaluation(obj)
        assert ev.measure == 0.0
        assert ev.orbit == obj
        assert ev.__reduce__() == (TestEvaluation, (obj,))
