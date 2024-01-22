# the analysis class can be extended to work with
# any arbitrary "evaluation function" of an orbit
# be overwriting __eval__

from commensurability.base import AnalysisBase


class FrequencyAnalysis(AnalysisBase):
    def __eval__(self, points):
        x, y, z = points.T

        # extract fundamenal frequencies
        f_x = 0
        f_y = 0
        f_z = 0

        return [f_x, f_y, f_z]


class FractalAnalysis(AnalysisBase):
    def __eval__(self, points):
        # do some fractal dimension analysis
        ...
