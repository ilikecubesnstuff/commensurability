# mypy: ignore-errors

import astropy.coordinates as c

from .base import AnalysisBase
from .tessellation import Tessellation


class TessellationAnalysis(AnalysisBase):
    dim = 3

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        tess = Tessellation(orbit.xyz.T)
        return tess.measure


class TessellationAnalysis2D(AnalysisBase):
    dim = 2

    @staticmethod
    def __eval__(orbit: c.SkyCoord) -> float:
        tess = Tessellation(orbit.xyz[:2].T)
        return tess.measure
