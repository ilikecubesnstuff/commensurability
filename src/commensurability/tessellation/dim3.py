import numpy as np
from scipy.linalg import norm
from scipy.spatial import ConvexHull

try:
    import matplotlib.pyplot as plt
    import mpl_toolkits.mplot3d as a3
    PLOTTING = True
except ImportError:
    PLOTTING = False

from . import generic
# from .dim2 import Tessellation as Tess2D


class Tessellation(generic.Tessellation):

    def normalization(self):
        # r = norm(self.points, axis=1)
        # return 4/3 * np.pi * np.max(r)**3

        # x, y, z = self.points.T
        # return np.pi * np.max(x**2 + y**2) * (np.max(z) - np.min(z))

        # x, y, z = self.points.T
        # R = np.sqrt(x**2 + y**2)
        # points = np.array([R, z]).T
        # points = np.array([*points, [0, max(z)], [0, min(z)]])
        # hull = ConvexHull(points)

        # poly = points[hull.vertices]
        # start = poly[0]
        # poly = poly[1:] - start

        # # NOTE: requires "pairwise" from itertools (recent python version)
        # centroids = [start + (t1 + t2)/3 for t1, t2 in pairwise(poly)]
        # areas = [np.linalg.det([t1, t2]) for t1, t2 in pairwise(poly)]

        # centroid = np.sum([a*c for c, a in zip(centroids, areas)], axis=0)
        # return 2 * np.pi * np.linalg.norm(centroid[:2])

        # hull = ConvexHull(self.points)
        # return hull.volume

        x, y, z = self.points.T
        r000 = np.array([+x, +y, z]).T
        r090 = np.array([-y, +x, z]).T
        r180 = np.array([-x, -y, z]).T
        r270 = np.array([+y, -x, z]).T

        points = np.array([*r000, *r090, *r180, *r270])
        hull = ConvexHull(points)
        return hull.volume

    @property
    def volume(self):
        return self.calculate_measure()

    @staticmethod
    def simplex_sides(*vertices):
        v1, v2, v3, v4 = vertices
        # return [
        #     norm(np.cross(v2-v1, v3-v1)),
        #     norm(np.cross(v2-v1, v4-v1)),
        #     norm(np.cross(v3-v1, v4-v1)),
        #     norm(np.cross(v3-v2, v4-v2)),
        #     Tess2D.simplex_measure(v1, v2-v1, v3-v1),
        #     Tess2D.simplex_measure(v1, v2-v1, v4-v1),
        #     Tess2D.simplex_measure(v1, v3-v1, v4-v1),
        #     Tess2D.simplex_measure(v2, v3-v2, v4-v2),
        # ]
        return [
            norm(v2 - v1),
            norm(v3 - v1),
            norm(v4 - v1),
            norm(v3 - v2),
            norm(v4 - v2),
            norm(v4 - v3),
        ]

    @staticmethod
    def simplex_measure(*vertices):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4) = vertices
        a1 = (x2-x1) * ((y3-y1) * (z4-z1) - (y4-y1) * (z3-z1))
        a2 = (x3-x1) * ((y4-y1) * (z2-z1) - (y2-y1) * (z4-z1))
        a3 = (x4-x1) * ((y2-y1) * (z3-z1) - (y3-y1) * (z2-z1))
        return abs(a1 + a2 + a3) / 6

    def plot_tessellation_trimming(self, plot_included=True, plot_removed=False, plot_points=True):
        """
        Plot the triangulation - trimmed triangles are drawn in red.
        """
        if not PLOTTING:
            raise ImportError('This method requires matplotlib.')

        x, y, z = self.points.T

        g_conns = set()
        r_conns = set()
        for simplex, included in zip(self.tri.simplices, self.mask):
            i1, i2, i3, i4 = sorted(simplex)
            conns = g_conns if included else r_conns
            conns.add((i1, i2))
            conns.add((i1, i3))
            conns.add((i1, i4))
            conns.add((i2, i3))
            conns.add((i2, i4))
            conns.add((i3, i4))

        ax = plt.figure().add_subplot(projection='3d')
        if plot_removed:
            r_lines = [(self.points[i1], self.points[i2]) for i1, i2 in r_conns]
            print(len(r_lines), 'lines added')
            line_collection = a3.art3d.Poly3DCollection(r_lines)
            line_collection.set_edgecolor('r')
            line_collection.set_linewidths(0.1)
            ax.add_collection3d(line_collection)
        if plot_included:
            g_lines = [(self.points[i1], self.points[i2]) for i1, i2 in g_conns]
            line_collection = a3.art3d.Poly3DCollection(g_lines)
            print(len(g_lines), 'lines added')
            line_collection.set_edgecolor('g')
            line_collection.set_linewidths(0.1)
            ax.add_collection3d(line_collection)
        if plot_points:
            ax.scatter(x, y, z, marker='.')
            print(len(x), 'points added')
        ax_lim = 1.1 * max(max(x), max(y), max(z))
        ax_lim = (-ax_lim, ax_lim)
        ax.set(
            xlim=ax_lim,
            ylim=ax_lim,
            zlim=ax_lim
        )
        plt.show()
