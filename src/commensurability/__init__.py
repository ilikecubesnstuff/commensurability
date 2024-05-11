from .base import AnalysisBase2D as _AnalysisBase2D
from .base import AnalysisBase3D as _AnalysisBase3D
from .tessellation import Tessellation as _Tessellation


class TessellationAnalysis(_AnalysisBase3D):
    evaluate = staticmethod(_Tessellation)


class TessellationAnalysis2D(_AnalysisBase2D):
    @staticmethod
    def evaluate(orbit):
        return _Tessellation(orbit.xyz[:2].T)
