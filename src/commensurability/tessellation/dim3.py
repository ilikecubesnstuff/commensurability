from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.axes3d import Axes3D

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
        v1, v2, v3, v4 = points[simplex]
        legs = [
            norm(v2 - v1),
            norm(v3 - v1),
            norm(v4 - v1),
            norm(v3 - v2),
            norm(v4 - v2),
            norm(v4 - v3),
        ]
        tracers['largest side'][i] = max(legs)
        tracers['smallest side'][i] = min(legs)

        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = v1, v2, v3
        tracers['area'][i] = abs(x1 * (y2 * z3 - y3 * z2) + x2 * (y3 * z1 - y1 * z3) + x3 * (y1 * z2 - y2 * z1)) / 6
    mask = np.ones(tri.nsimplex, dtype=np.bool_)

    # filter out elongated simplices
    threshold = 10 * np.median(tracers['smallest side'])
    mask *= (tracers['largest side'] < threshold)

    return tri.simplices, tracers, mask


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
    normalization = 4/3 * np.pi * max(r)**3
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
    x, y, z = points.T

    g_conns = set()
    r_conns = set()
    for simplex, included in zip(simplices, mask):
        i1, i2, i3, i4 = sorted(simplex)
        conns = g_conns if included else r_conns
        conns.add((i1, i2))
        conns.add((i1, i3))
        conns.add((i1, i4))
        conns.add((i2, i3))
        conns.add((i2, i4))
        conns.add((i3, i4))

    g_lines = [(points[i1], points[i2]) for i1, i2 in g_conns]
    # r_lines = [(points[i1], points[i2]) for i1, i2 in r_conns]
    
    ax = plt.figure().add_subplot(projection='3d')
    l = a3.art3d.Poly3DCollection(g_lines)
    l.set_edgecolor('g')
    ax.add_collection3d(l)
    # l = a3.art3d.Poly3DCollection(r_lines)
    # l.set_edgecolor('r')
    # ax.add_collection3d(l)
    ax.set(
        xlim = (1.1*min(x), 1.1*max(x)),
        ylim = (1.1*min(y), 1.1*max(y)),
        zlim = (1.1*min(z), 1.1*max(z))
    )
    plt.show()


def main():
    N = 1000
    k = 0.1
    angs = 2 * np.pi * np.random.random(N)
    x = np.cos(angs) + np.random.normal(0, k, N)
    y = np.sin(angs) + np.random.normal(0, k, N)
    z = x + y + np.random.normal(0, 0.1, N)
    points = np.array([x, y, z]).T

    simplices, tracers, mask = _tesselate_and_trim(points)
    print(_calculate_normalized_area(points, tracers, mask))
    plot_tessellation_trimming(points, simplices, mask)

if __name__=='__main__':
    main()