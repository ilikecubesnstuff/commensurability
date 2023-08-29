from __future__ import annotations
from itertools import combinations

import numpy as np
from scipy import spatial, linalg

from .base import TessellationBase


class TessellationGeneric(TessellationBase):

    @staticmethod
    def simplex_sides(*vertices):
        # combinatoric approach - not gonna use this in practice, hopefully
        return [v2 - v1 for v1, v2 in combinations(vertices, 2)]

    @staticmethod
    def simplex_measure(*vertices):
        # general simplex volume - not gonna use this in practice, hopefully
        first, *rest = vertices
        dim = len(first)
        mat = [v - first for v in rest]
        return linalg.det(mat) / np.math.factorial(dim)

    class Normalization(TessellationBase):

        def nsphere_approx(self) -> float:
            # stirling's approximation - not gonna use this in practice, hopefully
            d = self.points.shape[1]
            r = linalg.norm(self.points, axis=1)
            return 1 / np.sqrt(d * np.pi) * (2 * np.pi * np.e / d)**(d / 2) * np.max(r)**d

        def convexhull(self) -> float:
            # breaks for co-rotation cases
            points = self.tri.convex_hull
            return spatial.ConvexHull(points).volume

        def convexhull_rot4(self):
            x, y, *rest = self.points.T
            r000 = np.array([+x, +y, *rest]).T
            r090 = np.array([-y, +x, *rest]).T
            r180 = np.array([-x, -y, *rest]).T
            r270 = np.array([+y, -x, *rest]).T

            points = np.array([*r000, *r090, *r180, *r270])
            hull = spatial.ConvexHull(points)
            return hull.volume

        default = convexhull_rot4
