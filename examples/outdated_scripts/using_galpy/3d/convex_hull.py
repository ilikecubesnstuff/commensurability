from itertools import pairwise

import numpy as np
import matplotlib.pyplot as plt

from scipy.linalg import norm
from scipy.spatial import ConvexHull

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation



omega = 30 * u.km / u.s / u.kpc
POTENTIAL = [
    potential.NFWPotential(conc=10, mvir=1),
    potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc),
    potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
    potential.NonInertialFrameForce(Omega=omega)
]
ic = [
    8 * np.random.random() * u.kpc, 
    100 * np.random.random() * u.km / u.s, 
    200 * np.random.random() * u.km / u.s, 
    5 * np.random.random() * u.kpc, 
    0 * np.random.random() * u.km / u.s, 
    0 * np.random.random() * u.deg
]
ic = [
    3 * u.kpc, 
    0 * u.km / u.s, 
    150 * u.km / u.s, 
    1 * u.kpc, 
    0 * u.km / u.s, 
    0 * u.deg
]
print(ic)
ts = np.linspace(0, 2, 400) * u.Gyr
o = orbit.Orbit(ic)
o.integrate(ts, POTENTIAL, method='dopr54_c')

tess = Tessellation.from_galpy_orbit(o)
measure = tess.volume * tess.normalization()
print('orbit measure:', measure)


r = norm(tess.points, axis=1)
nc = 4/3 * np.pi * np.max(r)**3
print('sph', measure/nc)


x, y, z = tess.points.T
nc = np.pi * np.max(x**2 + y**2) * (np.max(z) - np.min(z))
print('cyl', measure/nc)


x, y, z = tess.points.T
R = np.sqrt(x**2 + y**2)
points = np.array([R, z]).T
# points = np.array([*points, [0, max(z)], [0, min(z)]])
hull = ConvexHull(points)

poly = points[hull.vertices]
start = poly[0]
poly = poly[1:] - start

plt.plot(R, z, 'k.')
istart = hull.vertices[0]
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
    a, b = simplex
    simplex = [istart, a]
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
    simplex = [istart, b]
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

centroids = [start + (t1 + t2)/3 for t1, t2 in pairwise(poly)]
areas = [(x1 * y2 - y1 * x2) / 2 for (x1, x2), (y1, y2) in pairwise(poly)]

for c, a in zip(centroids, areas):
    plt.plot([c[0]], [c[1]], 'g^', markersize=a*100/hull.volume)

centroid = np.sum([a*c for c, a in zip(centroids, areas)], axis=0)

x, y = start
plt.plot([x], [y], 'bo')

x, y = centroid/hull.volume
plt.plot([x], [y], 'ro')

nc = 2 * np.pi * np.linalg.norm(centroid[:2])
print('cvh', measure/nc)


x, y, z = tess.points.T
R = np.sqrt(x**2 + y**2)
points = np.array([R, z]).T
points = np.array([*points, [0, max(z)], [0, min(z)]])
hull = ConvexHull(points)

poly = points[hull.vertices]
start = poly[0]
poly = poly[1:] - start

plt.plot(R, z, 'k.')
istart = hull.vertices[0]
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
    a, b = simplex
    simplex = [istart, a]
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
    simplex = [istart, b]
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

centroids = [start + (t1 + t2)/3 for t1, t2 in pairwise(poly)]
areas = [(x1 * y2 - y1 * x2) / 2 for (x1, x2), (y1, y2) in pairwise(poly)]

for c, a in zip(centroids, areas):
    plt.plot([c[0]], [c[1]], 'g^', markersize=a*100/hull.volume)

centroid = np.sum([a*c for c, a in zip(centroids, areas)], axis=0)

x, y = start
plt.plot([x], [y], 'bo')

x, y = centroid/hull.volume
plt.plot([x], [y], 'ro')

nc = 2 * np.pi * np.linalg.norm(centroid[:2])
print('cvhf', measure/nc)
plt.show()


hull = ConvexHull(tess.points)
nc = hull.volume
print('cvh3d', measure/nc)


x, y, z = tess.points.T
r000 = np.array([ x,  y, z]).T
r090 = np.array([-y,  x, z]).T
r180 = np.array([-x, -y, z]).T
r270 = np.array([ y, -x, z]).T

points = np.array([*r000, *r090, *r180, *r270])
hull = ConvexHull(points)
nc = hull.volume
print('cvh3dc', measure/nc)


tess.plot_tessellation_trimming()
plt.show()

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.scatter(x, y, z)
for s in hull.simplices:
    ax.plot(points[s, 0], points[s, 1], points[s, 2], 'r-')
plt.show()