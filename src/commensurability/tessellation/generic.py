from collections import defaultdict
from itertools import combinations

import numpy as np
from scipy.spatial import Delaunay
from scipy.linalg import norm, det


class Tessellation:

    def __init__(self, points, trim=10):
        points = np.array(points)
        self.points = points

        # tessellation
        self.tri = Delaunay(points)

        # trimming
        if trim:
            self.calculate_trimming(axis_ratio=trim)

    def calculate_trimming(self, axis_ratio=10):
        # compute important quantities (stored in "tracers")
        self.tracers = defaultdict(lambda: np.zeros(self.tri.nsimplex))
        for i, simplex in enumerate(self.tri.simplices):
            vertices = self.points[simplex]

            # store side lengths (for trimming)
            sides = self.simplex_sides(*vertices)
            self.tracers['largest side'][i] = max(sides)
            self.tracers['smallest side'][i] = min(sides)

            # store simplex measures
            self.tracers['measure'][i] = self.simplex_measure(*vertices)
        self.mask = np.ones(self.tri.nsimplex, dtype=np.bool_)

        # trim simplices with large sides
        threshold = axis_ratio * np.median(self.tracers['smallest side'])
        self.mask *= (self.tracers['largest side'] < threshold)

    def normalization(self):
        # stirling's approximation - not gonna use this in practice, hopefully
        d = self.points.shape[1]
        r = norm(self.points, axis=1)
        return 1 / np.sqrt(d * np.pi) * (2 * np.pi * np.e / d)**(d / 2) * np.max(r)**d

    def calculate_measure(self):
        # calculate normalized measure
        return np.sum(self.tracers['measure'][self.mask]) / self.normalization()

    @staticmethod
    def simplex_sides(*vertices):
        # combinatoric approach - not gonna use this in practice, hopefully
        return [norm(v2 - v1) for v1, v2 in combinations(vertices, 2)]

    @staticmethod
    def simplex_measure(*vertices):
        # general simplex volume - not gonna use this in practice, hopefully
        first, *rest = vertices
        d = len(first)
        mat = [v - first for v in rest]
        return det(mat) / np.math.factorial(d)
