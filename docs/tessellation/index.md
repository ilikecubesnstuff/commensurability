# Home Page for `commensurability.tessellation`

Although this is a subpackage of `commensurability`, it implements functionality that can extended beyond exclusive usage
with the parent package; it can be used for standalone research.
See [usage](usage/index.md) for both usage cases.

This subpackage is compatible with the galactic dynamics packages [`agama`](https://github.com/GalacticDynamics-Oxford/Agama), [`gala`](https://gala-astro.readthedocs.io/en/latest/), and [`galpy`](https://docs.galpy.org/en/latest/).

## Attribution

This package implements and extends the algorithm presented by [Petersen, Weinberg & Katz (2020)](https://academic.oup.com/mnras/article/500/1/838/5925365).
From appendix B1 of ["Using commensurabilities and orbit structure to understand barred galaxy evolution"](https://academic.oup.com/mnras/article/500/1/838/5925365):

> Given a series of samples at discrete times for an orbit, we wish to approximate the area that an orbit would sample in the theoretical limit where the time interval between points in the series goes to zero, $\delta t \to 0$ and the total time integration is very long, $T \to \infty$.
> To measure the area of an annulus or volume of a sphere that a discrete set of orbit time samples would eventually fill as $T \to \infty$, we require a tessellation technique that transforms a discrete time series of points into an integrable area, $\delta t \to 0$.
> One such computational technique is Delaunay triangulation (DT).
> We construct a procedure that uses DT, taking as input a set of points and returning a single value that is the (normalized) computed orbit area from the sum of individual tessellated triangles.

A generalized N-dimensional algorithm is implemented, but the 2D and 3D case implement special cases.
This package also offers a variety of normalization options.
See [implementation](implementation.md) for details.
