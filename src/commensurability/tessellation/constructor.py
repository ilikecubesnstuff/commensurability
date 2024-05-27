"""
This module provides the main function of the package for performing the
tessellation and trimming algorithm on an arbitrary collection of points.
"""

from __future__ import annotations

import inspect
from typing import Any, Optional

import astropy.coordinates as c
import numpy as np

from .base import TessellationBase as _TessType
from .dim2 import Tessellation2D as _Tess2D
from .dim3 import Tessellation3D as _Tess3D
from .exceptions import LowDimensionalityException
from .generic import TessellationGeneric as _TessND


def Tessellation(
    orbit_or_point_array: Any,
    dims_for_orbit: Optional[tuple[str]] = None,
    *,
    incremental: bool = True,
    qhull_options: Optional[str] = None,
    axis_ratio: float = 10,
    normalization_routine: str = "default",
    verbosity: int = 0,
) -> _TessType:
    """
    Perform a tessellation and trimming on a collection of points or orbit object (from `galpy` or `gala`).

    This function returns a tessellation object based on the dimensionality of the points.
    If an orbit object is passed, the dimensions to extract must be specified by name in a tuple.

    Args:
        orbit_or_point_array (Any): Input data, which can be an orbit object or a 2D array of shape (npoints, ndim).
        dims_for_orbit (Optional[tuple[str]], optional): Dimension names for orbit objects (default None).
        incremental (bool, optional): Whether to use incremental Delaunay triangulation (default True).
        qhull_options (str, optional): Additional options for Qhull (default None).
        axis_ratio (float, optional): Threshold for tessellation trimming (default 10).
        normalization_routine (str, optional): The normalization routine to use (default "default").
        verbosity (int, optional): Verbosity level (default 0).

    Returns:
        TessellationBase: A tessellation object of the appropriate dimensionality.

    Raises:
        LowDimensionalityException: If the input data has an unsupported dimensionality (less than 2).
    """
    points = orbit = orbit_or_point_array

    pkg = None
    module = inspect.getmodule(orbit)
    if module:
        pkg, *_ = module.__name__.partition(".")

    if pkg in ("galpy", "gala", "agama"):
        orbit = orbit_or_point_array
        if dims_for_orbit is None:
            raise TypeError("Orbit dimensions must be supplied if tessellating an orbit object")
        if pkg == "galpy":
            axes = [getattr(orbit, dim) for dim in dims_for_orbit]
            points = np.array([ax(orbit.t) for ax in axes]).T
        elif pkg == "gala":
            points = np.array([getattr(orbit, dim).value for dim in dims_for_orbit]).T
        elif pkg == "agama":
            raise NotImplementedError()
    else:
        if dims_for_orbit is not None:
            raise ValueError("Orbit dimensions must only be passed with an orbit object")
        if isinstance(
            orbit, c.CartesianRepresentation
        ):  # NOTE: seems like a hacky fix, works for now
            points = orbit.xyz.T
        points = np.array(points, dtype=float)

    if points.ndim != 2:
        raise ValueError(
            "Tessellation can only be performed on a 2D array of shape (npoints, ndim)"
        )

    init_args = dict(
        points=points,
        incremental=incremental,
        qhull_options=qhull_options,
        axis_ratio=axis_ratio,
        normalization_routine=normalization_routine,
        verbosity=verbosity,
    )

    # NOTE: ndim is not the same as points.ndim
    *_, ndim = points.shape
    if ndim == 2:
        return _Tess2D(**init_args)
    elif ndim == 3:
        return _Tess3D(**init_args)
    elif ndim > 3:
        return _TessND(**init_args)
    else:
        raise LowDimensionalityException(
            "Unsupported dimensionality, requires dimension 2 or greater"
        )
