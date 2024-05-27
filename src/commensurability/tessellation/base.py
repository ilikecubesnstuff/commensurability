"""
This module defines the abstract base class `TessellationBase` used for
2D, 3D and general N-D tessellation algorithms.
"""

from __future__ import annotations

import warnings
from abc import abstractmethod
from collections import defaultdict
from typing import Any, Callable, Mapping, Optional, Union

import numpy as np
from scipy import spatial

from ..evaluation import Evaluation

MISSING = object()


def MISSING_METHOD() -> None:
    pass


class FailedDelaunay:
    """
    A class representing a failed Delaunay triangulation.
    This is used in the case of a degenerate or co-spherical collections of points.
    """

    def __init__(self):
        self.nsimplex = 0
        self.simplices = [[0]]
        self.convex_hull = [[0]]


class TessellationBase(Evaluation):
    """
    A base class for the tessellation and trimming algorithm.
    """

    __slots__ = (
        "points",
        "_normalizations",
        "tri",
        "tracers",
        "mask",
        "normalization_const",
        "measure",
    )

    def __init__(
        self,
        points: np.ndarray,
        *,
        incremental: bool = True,
        qhull_options: Optional[str] = None,
        axis_ratio: float = 10,
        normalization_routine: str = "default",
        verbosity: int = 0,
    ) -> None:
        """
        This is an abstract base class - use `generic.TessellationGeneric` for general collections of points.

        Args:
            points (np.ndarray): The input points for tessellation.
            incremental (bool, optional): Whether to use incremental Delaunay triangulation (default True).
            qhull_options (str, optional): Additional options for Qhull (default None).
            axis_ratio (float, optional): Threshold for tessellation trimming (default 10).
            normalization_routine (str, optional): The normalization routine to use (default "default").
            verbosity (int, optional): Verbosity level (default 0).

        """
        self.points: np.ndarray = points
        self._normalizations: Mapping[str, Callable]
        self.tri: Union[spatial.Delaunay, FailedDelaunay]
        self.tracers: Mapping[str, np.ndarray]
        self.mask: Optional[np.ndarray]
        self.normalization_const: float
        self.measure: float
        verbosity = verbosity

        normalization_class = getattr(self, "Normalization", type("Normalization", (), {}))
        self._normalizations = dict(vars(normalization_class))
        if hasattr(self._normalizations, "__module__"):
            del self._normalizations["__module__"]
        if hasattr(self._normalizations, "__dict__"):
            del self._normalizations["__dict__"]
        if hasattr(self._normalizations, "__weakref__"):
            del self._normalizations["__weakref__"]
        if hasattr(self._normalizations, "__doc__"):
            del self._normalizations["__doc__"]

        try:
            r = self._compute_delaunay(incremental, qhull_options)
            if verbosity:
                if self.tri:
                    print(f"{self.__class__.__name__}: Delaunay tessellation computed.")
                else:
                    print(f"{self.__class__.__name__}: Delaunay tessellation failed. {r}")

            self._compute_tracers()
            if verbosity:
                print(f"{self.__class__.__name__}: Simplex sides and measures computed.")

            self._compute_trimming(axis_ratio)
            if verbosity:
                print(f"{self.__class__.__name__}: Tessellation trimming computed.")

            self._compute_normalization(normalization_routine)
            if verbosity:
                print(f"{self.__class__.__name__}: Normalization computed.")

            self.measure = np.sum(self.tracers["measure"][self.mask]) / self.normalization_const
        except AttributeError:
            warnings.warn(
                "Point set appears to be degenerate or co-spherical. "
                "Consider using a different dimensionality for the degenerate case."
            )

    def __repr__(self):
        status = "bare"
        if self.tri is not None:
            status = "triangulated"
        if self.mask is not None:
            status = "trimmed"
        if self.measure is not None:
            status = f"measure={self.measure}"
        return f"{self.__class__.__name__}[{status}]"

    def __setattr__(self, name: str, value: Any) -> None:
        existing_value = getattr(self, name, MISSING)
        if existing_value is not MISSING:
            raise AttributeError(
                f"Attribute {name} is already set to {existing_value}. "
                f"Please create a new Tessellation object for this operation. "
            )
        return super().__setattr__(name, value)

    def _compute_delaunay(
        self, incremental: bool, qhull_options: Optional[str]
    ) -> Optional[spatial.QhullError]:
        try:
            # Delaunay triangulation routine from SciPy:
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html
            self.tri = spatial.Delaunay(
                self.points, incremental=incremental, qhull_options=qhull_options
            )
            return None
        except spatial.QhullError as e:
            # For degenerate cases, proceed with measure of 0
            self.tri = FailedDelaunay()
            # self.tri = None  # NOTE: might break when incremental=True
            self.tracers = defaultdict(lambda: np.zeros(self.tri.nsimplex))
            self.mask = None
            self.normalization_const = 1.0
            self.measure = 0.0
            return e

    def _compute_tracers(self) -> None:
        self.tracers = defaultdict(lambda: np.zeros(self.tri.nsimplex))
        for i, simplex in enumerate(self.tri.simplices):
            vertices = self.points[simplex]

            # store extreme side lengths (for trimming)
            side_lens = self.simplex_sides(*vertices)
            self.tracers["largest side"][i] = max(side_lens)
            self.tracers["smallest side"][i] = min(side_lens)

            # store simplex measures
            self.tracers["measure"][i] = self.simplex_measure(*vertices)

    def _compute_trimming(self, axis_ratio: float = 10) -> None:
        # trim simplices with large sides
        threshold = axis_ratio * np.median(self.tracers["smallest side"])
        self.mask = self.tracers["largest side"] < threshold

    def _compute_normalization(self, routine: str) -> None:
        normalization_method: Callable = self._normalizations.get(routine, MISSING_METHOD)
        if normalization_method is MISSING_METHOD:
            message = f"Unrecognized normalization routine {routine}. "
            available = list(self._normalizations.keys())
            if available:
                message += f"Available normalizations are {available}"
            else:
                message += "No available normalizations for this class"
            raise ValueError(message)
        self.normalization_const = normalization_method(self)

    @staticmethod
    @abstractmethod
    def simplex_sides(*vertices: np.ndarray) -> list[float]:
        """
        Calculate the side lengths of a simplex.
        This must be redefined in a base class.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            List[float]: A list of side lengths.
        """
        return []

    @staticmethod
    @abstractmethod
    def simplex_measure(*vertices: np.ndarray) -> float:
        """
        Calculate the measure of a simplex.
        This must be redefined in a base class.

        Args:
            *vertices: The vertices of the simplex.

        Returns:
            float: The measure of the simplex.
        """
        return 0.0

    def plot(self, ax):
        """
        Plot the tessellation.

        Args:
            ax (matplotlib.axes._axes.Axes): Matplotlib axes (default None).
        """
        pass
