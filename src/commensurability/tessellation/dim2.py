import numpy as np
from scipy.linalg import norm

try:
    import matplotlib.pyplot as plt
    PLOTTING = True
except ImportError:
    PLOTTING = False

from . import generic


class Tessellation(generic.Tessellation):

    def normalization(self):
        r = norm(self.points, axis=1)
        return np.pi * (max(r)**2)

    @property
    def area(self):
        return self.calculate_measure()

    @staticmethod
    def simplex_sides(*vertices):
        v1, v2, v3 = vertices
        return [
            norm(v2 - v1),
            norm(v3 - v1),
            norm(v3 - v2),
        ]

    @staticmethod
    def simplex_measure(*vertices):
        (x1, y1), (x2, y2), (x3, y3) = vertices
        return abs((x2-x1) * (y3-y1) - (x3-x1) * (y2-y1)) / 2

    def plot_tessellation_trimming(self, plot_included=True, plot_removed=False, plot_points=True):
        """
        Plot the triangulation - trimmed triangles are drawn in red.
        """
        if not PLOTTING:
            raise ImportError('This method requires matplotlib.')

        x, y = self.points.T
        if plot_removed:
            plt.triplot(x, y, self.tri.simplices, mask=self.mask, color='red')
        if plot_included:
            plt.triplot(x, y, self.tri.simplices, mask=~self.mask, color='green')
        if plot_points:
            plt.plot(x, y, 'k.', markersize=0.1)
        plt.show()
