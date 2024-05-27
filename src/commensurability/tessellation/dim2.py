"""
This module implements a 2D tessellation and trimming algorithm in the `Tessellation2D` class.
This module is part of the tessellation package and can be used for 2D orbit tessellation tasks.

It inherits from `TessellationBase` and includes methods for calculating triangle side lengths
and triangle areas. The `Normalization` nested class includes normalization methods.
Additionally, the class offers a plotting function to visualize the tessellation.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import linalg

from .base import TessellationBase


class Tessellation2D(TessellationBase):
    """
    A class for the tessellation and trimming algorithm applied in 2 dimensions.
    """

    @staticmethod
    def simplex_sides(*vertices: np.ndarray) -> list:
        """
        Compute the side lengths of a 2D simplex defined by its vertices.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            list: List of side lengths.

        """
        v1, v2, v3 = vertices
        return [
            linalg.norm(v2 - v1),
            linalg.norm(v3 - v1),
            linalg.norm(v3 - v2),
        ]

    @staticmethod
    def simplex_measure(*vertices: np.ndarray) -> float:
        """
        Compute the measure (area) of a 2D simplex defined by its vertices.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            float: The area of the simplex.

        """
        (x1, y1), (x2, y2), (x3, y3) = vertices
        return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2

    class Normalization:
        """
        A class providing various methods for normalization in 2D.

        Methods:
            circle: Compute the area of a circle containing the points.
            default: Default normalization method (circle).
        """

        points: np.ndarray

        def circle(self) -> float:
            """
            Compute the area of a circle containing the points.

            Returns:
                float: Area of the circle.
            """
            r = linalg.norm(self.points, axis=1)
            return np.pi * (max(r) ** 2)

        default = circle

    @property
    def area(self) -> float:
        """
        Alias for `measure`.

        Returns:
            float: Area of the tessellation (same as measure).
        """
        return self.measure

    def plot(self, ax, plot_included=True, plot_removed=False, plot_points=True):
        """
        Plot the 2D tessellation.
        Included triangles are green, excluded triangles are red.

        Args:
            ax (matplotlib.axes._axes.Axes): Matplotlib axes.
            plot_included (bool, optional): Whether to plot included triangles (default True).
            plot_removed (bool, optional): Whether to plot removed triangles (default False).
            plot_points (bool, optional): Whether to plot points (default True).

        Raises:
            RuntimeError: If tessellation failed.
        """
        if self.tri is None:
            raise RuntimeError("Tessellation failed; cannot produce tessellation plot")

        X, Y = self.points.T
        plotted_objects = set()
        if plot_removed:
            lines, markers = plt.triplot(X, Y, self.tri.simplices, mask=self.mask, color="red")
            plotted_objects.add(lines)
            plotted_objects.add(markers)
        if plot_included:
            lines, markers = plt.triplot(X, Y, self.tri.simplices, mask=~self.mask, color="green")
            plotted_objects.add(lines)
            plotted_objects.add(markers)
        if plot_points:
            (points,) = plt.plot(X, Y, "k.", markersize=0.5)
            plotted_objects.add(points)
        return plotted_objects
