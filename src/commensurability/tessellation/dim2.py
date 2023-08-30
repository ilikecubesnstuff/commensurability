import numpy as np
from scipy import linalg

try:
    import matplotlib.pyplot as plt
    PLOTTING = True
except ImportError:
    PLOTTING = False

from .generic import TessellationGeneric


class Tessellation2D(TessellationGeneric):

    @staticmethod
    def simplex_sides(*vertices):
        v1, v2, v3 = vertices
        return [
            linalg.norm(v2 - v1),
            linalg.norm(v3 - v1),
            linalg.norm(v3 - v2),
        ]

    @staticmethod
    def simplex_measure(*vertices):
        (x1, y1), (x2, y2), (x3, y3) = vertices
        return abs((x2-x1) * (y3-y1) - (x3-x1) * (y2-y1)) / 2

    class Normalization:

        def circle(self):
            r = linalg.norm(self.points, axis=1)
            return np.pi * (max(r)**2)

        default = circle

    @property
    def area(self):
        return self.measure

    def plot(self, plot_included=True, plot_removed=False, plot_points=True, verbosity=1, ax=None, show=True):
        """
        Plot the triangulation - trimmed triangles are drawn in red.
        """
        if not PLOTTING:
            raise ImportError('This method requires matplotlib')
        if self.tri is None:
            raise RuntimeError('Tessellation failed; cannot produce tessellation plot')

        if not ax:
            fig = plt.figure()
            ax = fig.add_subplot()
        X, Y = self.points.T

        if plot_removed:
            plt.triplot(X, Y, self.tri.simplices, mask=self.mask, color='red')
            if verbosity:
                print(self.__class__.__name__, 'plotting excluded edges (red):', len(self.mask))

        if plot_included:
            plt.triplot(X, Y, self.tri.simplices, mask=~self.mask, color='green')
            if verbosity:
                print(self.__class__.__name__, 'plotting included edges (green):', len(~self.mask))

        if plot_points:
            plt.plot(X, Y, 'k.', markersize=0.5)
            if verbosity:
                print(self.__class__.__name__, 'plotting points:', len(X))

        if show:
            plt.show()
        return ax
