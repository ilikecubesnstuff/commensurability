import numpy as np
from scipy import linalg, spatial

try:
    import matplotlib.pyplot as plt
    import mpl_toolkits.mplot3d as a3
    PLOTTING = True
except ImportError:
    PLOTTING = False

from .generic import TessellationGeneric


class Tessellation3D(TessellationGeneric):

    @staticmethod
    def simplex_sides(*vertices):
        v1, v2, v3, v4 = vertices
        return [
            linalg.norm(v2 - v1),
            linalg.norm(v3 - v1),
            linalg.norm(v4 - v1),
            linalg.norm(v3 - v2),
            linalg.norm(v4 - v2),
            linalg.norm(v4 - v3),
        ]

    @staticmethod
    def simplex_measure(*vertices):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4) = vertices
        a1 = (x2-x1) * ((y3-y1) * (z4-z1) - (y4-y1) * (z3-z1))
        a2 = (x3-x1) * ((y4-y1) * (z2-z1) - (y2-y1) * (z4-z1))
        a3 = (x4-x1) * ((y2-y1) * (z3-z1) - (y3-y1) * (z2-z1))
        return abs(a1 + a2 + a3) / 6

    class Normalization:

        def sphere(self):
            r = linalg.norm(self.points, axis=1)
            return 4/3 * np.pi * np.max(r)**3

        def cylinder(self):
            x, y, z = self.points.T
            return np.pi * np.max(x**2 + y**2) * (np.max(z) - np.min(z))

        def Rz_convexhull(self):
            x, y, z = self.points.T
            R = np.sqrt(x**2 + y**2)
            points = np.array([R, z]).T
            points = np.array([*points, [0, max(z)], [0, min(z)]])
            hull = spatial.ConvexHull(points)

            poly = points[hull.vertices]
            start = poly[0]
            poly = poly[1:] - start

            # NOTE: requires "pairwise" from itertools (recent python version)
            from itertools import pairwise
            centroids = [start + (t1 + t2)/3 for t1, t2 in pairwise(poly)]
            areas = [np.linalg.det([t1, t2]) for t1, t2 in pairwise(poly)]

            centroid = np.sum([a*c for c, a in zip(centroids, areas)], axis=0)
            return 2 * np.pi * np.linalg.norm(centroid[:2])

        def convexhull(self):
            hull = spatial.ConvexHull(self.points)
            return hull.volume

        def convexhull_rot4(self):
            x, y, z = self.points.T
            r000 = np.array([+x, +y, z]).T
            r090 = np.array([-y, +x, z]).T
            r180 = np.array([-x, -y, z]).T
            r270 = np.array([+y, -x, z]).T

            points = np.array([*r000, *r090, *r180, *r270])
            hull = spatial.ConvexHull(points)
            return hull.volume

        default = convexhull_rot4

    @property
    def volume(self):
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
            ax = fig.add_subplot(projection='3d')
        X, Y, Z = self.points.T

        included_edges = set()
        excluded_edges = set()
        for simplex, included in zip(self.tri.simplices, self.mask):
            i1, i2, i3, i4 = simplex
            edges = included_edges if included else excluded_edges
            for tuplet in (
                (i1, i2),
                (i1, i3),
                (i1, i4),
                (i2, i3),
                (i2, i4),
                (i3, i4),
            ):
                edges.add(tuplet)

        if plot_removed and plot_included:
            inex_edges = included_edges & excluded_edges
            included_edges -= inex_edges
            excluded_edges -= inex_edges

            inex_lines = [(self.points[i1], self.points[i2]) for i1, i2 in inex_edges]
            if verbosity:
                print(self.__class__.__name__, 'plotting intersection edges (orange):', len(inex_lines))

            line_collection = a3.art3d.Poly3DCollection(inex_lines)
            line_collection.set_edgecolor('blue')
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)

        if plot_removed:
            excluded_lines = [(self.points[i1], self.points[i2]) for i1, i2 in excluded_edges]
            if verbosity:
                print(self.__class__.__name__, 'plotting excluded edges (red):', len(excluded_lines))

            line_collection = a3.art3d.Poly3DCollection(excluded_lines)
            line_collection.set_edgecolor('red')
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)

        if plot_included:
            included_lines = [(self.points[i1], self.points[i2]) for i1, i2 in included_edges]
            if verbosity:
                print(self.__class__.__name__, 'plotting included edges (green):', len(included_lines))

            line_collection = a3.art3d.Poly3DCollection(included_lines)
            line_collection.set_edgecolor('green')
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)

        if plot_points:
            ax.scatter(X, Y, Z, marker='.', color='black')
            if verbosity:
                print(self.__class__.__name__, 'plotting points:', len(X))

        ax_lim = 1.1 * max(max(X), max(Y), max(Z))
        ax_lim = (-ax_lim, ax_lim)
        ax.set(xlim=ax_lim, ylim=ax_lim, zlim=ax_lim)

        if show:
            plt.show()
        return ax
