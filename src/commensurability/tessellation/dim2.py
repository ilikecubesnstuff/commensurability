from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import Delaunay
from scipy.linalg import norm

from tqdm import tqdm


def _tesselate_and_trim(points):
    """
    Given a sequence of points, generate a Delaunay tessellation and
    a mask to remove large and/or high-axis-ratio simplices.
    """
    tri = Delaunay(points)
    tracers = defaultdict(lambda: np.zeros(tri.nsimplex))
    for i, simplex in tqdm(enumerate(tri.simplices), total=tri.nsimplex):
        v1, v2, v3 = points[simplex]
        legs = [norm(v2 - v1), norm(v3 - v2), norm(v1 - v3)]
        tracers['largest side'][i] = max(legs)
        tracers['smallest side'][i] = min(legs)

        (x1, y1), (x2, y2), (x3, y3) = v1, v2, v3
        tracers['area'][i] = ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
    mask = np.ones(tri.nsimplex, dtype=np.bool_)

    # filter out elongated simplices
    threshold = 10 * np.median(tracers['smallest side'])
    mask *= (tracers['largest side'] < threshold)

    return tri.simplices, tracers, ~mask


def tessellated(points):
    """
    Return Deluanay triangulation of the orbit and its trimming mask.
    """
    simplices, _, mask = _tesselate_and_trim(points)
    return simplices, mask


def _calculate_normalized_area(points, tracers, mask):
    """
    Document code here.
    """
    r = norm(points, axis=1)
    normalization = np.pi * (max(r)**2)
    areas = tracers['area']
    return np.sum(areas[mask]) / normalization

def normalized_area(points):
    """
    Return the normalized orbit area.
    """
    _, tracers, mask = _tesselate_and_trim(points)
    return _calculate_normalized_area(points, tracers, mask)

def normalized_areas(*point_sequences):
    """
    Return a list of the normalized orbit area for many orbits.
    """
    norm_areas = []
    for points in point_sequences:
        _, tracers, mask = _tesselate_and_trim(points)
        norm_areas.append(
            _calculate_normalized_area(points, tracers, mask)
        )
    return norm_areas

def normalized_area_generator(points_gen):
    """
    Yield orbit areas from a generator of point arrays.
    """
    for points in points_gen:
        _, tracers, mask = _tesselate_and_trim(points)
        yield _calculate_normalized_area(points, tracers, mask)


def plot_tessellation_trimming(points, simplices, mask):
    """
    Plot the triangulation - trimmed triangles are drawn in red.
    """
    x, y = points.T

    plt.triplot(x, y, simplices, mask=~mask, color='red')
    plt.triplot(x, y, simplices, mask=mask, color='green')
    plt.plot(x, y, 'k.', markersize=0.1)
    plt.show()


def main():
    N = 1000
    k = 0.05
    angs = 2 * np.pi * np.random.random(N)
    x = np.cos(angs) + np.random.normal(0, k, N)
    y = np.sin(angs) + np.random.normal(0, k, N)
    points = np.array([x, y]).T

    simplices, tracers, mask = _tesselate_and_trim(points)
    print(_calculate_normalized_area(points, tracers, mask))
    plot_tessellation_trimming(points, simplices, mask)

if __name__=='__main__':
    main()