"""
This module implements a 3D tessellation and trimming algorithm in the `Tessellation3D` class.
This module is part of the tessellation package and can be used for 3D orbit tessellation tasks.

It inherits from `TessellationBase` and includes methods for calculating tetrahedron side lengths
and tetrahedron volumes. The `Normalization` nested class includes normalization methods.
Additionally, the class offers a plotting function to visualize the tessellation.
"""

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
import numpy as np
from scipy import linalg, spatial

from .base import TessellationBase


class Tessellation3D(TessellationBase):
    """
    A class for the tessellation and trimming algorithm applied in 3 dimensions.
    """

    @staticmethod
    def simplex_sides(*vertices: np.ndarray) -> list:
        """
        Compute the side lengths of a 3D simplex defined by its vertices.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            list: List of side lengths.

        """
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
    def simplex_measure(*vertices: np.ndarray) -> float:
        """
        Compute the measure (volume) of a 3D simplex defined by its vertices.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            float: The volume of the simplex.

        """
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4) = vertices
        a1 = (x2 - x1) * ((y3 - y1) * (z4 - z1) - (y4 - y1) * (z3 - z1))
        a2 = (x3 - x1) * ((y4 - y1) * (z2 - z1) - (y2 - y1) * (z4 - z1))
        a3 = (x4 - x1) * ((y2 - y1) * (z3 - z1) - (y3 - y1) * (z2 - z1))
        return abs(a1 + a2 + a3) / 6

    class Normalization:
        """
        A class providing various methods for normalization in 3D.

        Methods:
            sphere: Compute the volume of a sphere containing the points.
            cylinder: Compute the volume of a cylinder containing the points.
            Rz_convexhull: Compute the volume of the convex hull in the R vs z plane rotated around the z-axis.
            convexhull: Compute the volume of the convex hull of the points.
            convexhull_rot4: Compute the volume of the convex hull of the points including copied rotations by 90 degrees four times.
            default: Default normalization method (convexhull_rot4).
        """

        points: np.ndarray

        def sphere(self) -> float:
            """
            Compute the volume of a sphere containing the points.

            Returns:
                float: Volume of the sphere.
            """
            r = linalg.norm(self.points, axis=1)
            return 4 / 3 * np.pi * np.max(r) ** 3

        def cylinder(self) -> float:
            """
            Compute the volume of a cylinder containing the points.

            Returns:
                float: Volume of the cylinder.
            """
            x, y, z = self.points.T
            return np.pi * np.max(x**2 + y**2) * (np.max(z) - np.min(z))

        def Rz_convexhull(self) -> float:
            """
            Compute the volume of the convex hull in the R vs z plane rotated around the z-axis.

            Returns:
                float: Volume of the convex hull after rotation.
            """
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

            centroids = [start + (t1 + t2) / 3 for t1, t2 in pairwise(poly)]
            areas = [np.linalg.det([t1, t2]) for t1, t2 in pairwise(poly)]

            centroid = np.sum([a * c for c, a in zip(centroids, areas)], axis=0)
            return 2 * np.pi * float(np.linalg.norm(centroid[:2]))

        def convexhull(self) -> float:
            """
            Compute the volume of the convex hull of the points.

            Returns:
                float: Volume of the convex hull.

            Note:
                This method may not work correctly for co-rotation cases.
            """
            hull = spatial.ConvexHull(self.points)
            return hull.volume

        def convexhull_rot4(self) -> float:
            """
            Compute the volume of the convex hull of the points including copied rotations by 90 degrees four times.

            Returns:
                float: Volume of the convex hull.
            """
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
    def volume(self) -> float:
        """
        Alias for `measure`.

        Returns:
            float: Volume of the tessellation (same as measure).
        """
        return self.measure

    def plot(self, ax, plot_included=True, plot_removed=False, plot_points=True):
        """
        Plot the 3D tessellation.
        Included tetrahedra are green, excluded tetrahedra are red.
        Shared edges are blue.

        Args:
            ax (mpl_toolkits.mplot3d.axes3d.Axes3D): Matplotlib 3D axes.
            plot_included (bool, optional): Whether to plot included triangles (default True).
            plot_removed (bool, optional): Whether to plot removed triangles (default False).
            plot_points (bool, optional): Whether to plot points (default True).

        Raises:
            RuntimeError: If tessellation failed.
        """
        if self.tri is None:
            raise RuntimeError("Tessellation failed; cannot produce tessellation plot")

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

        plotted_objects = set()

        if plot_removed and plot_included:
            inex_edges = included_edges & excluded_edges
            included_edges -= inex_edges
            excluded_edges -= inex_edges

            inex_lines = [(self.points[i1], self.points[i2]) for i1, i2 in inex_edges]

            line_collection = a3.art3d.Poly3DCollection(inex_lines)
            line_collection.set_edgecolor("blue")
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)
            plotted_objects.add(line_collection)

        if plot_removed:
            excluded_lines = [(self.points[i1], self.points[i2]) for i1, i2 in excluded_edges]

            line_collection = a3.art3d.Poly3DCollection(excluded_lines)
            line_collection.set_edgecolor("red")
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)
            plotted_objects.add(line_collection)

        if plot_included:
            included_lines = [(self.points[i1], self.points[i2]) for i1, i2 in included_edges]

            line_collection = a3.art3d.Poly3DCollection(included_lines)
            line_collection.set_edgecolor("green")
            line_collection.set_linewidths(0.2)
            ax.add_collection3d(line_collection)
            plotted_objects.add(line_collection)

        if plot_points:
            line = ax.scatter(X, Y, Z, marker=".", color="black")
            plotted_objects.add(line)

        ax_lim = 1.1 * max(max(X), max(Y), max(Z))
        ax_lim = (-ax_lim, ax_lim)
        ax.set(xlim=ax_lim, ylim=ax_lim, zlim=ax_lim)

        return plotted_objects
