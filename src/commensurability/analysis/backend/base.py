from __future__ import annotations

from abc import abstractmethod, abstractstaticmethod
from itertools import pairwise, islice
import typing

import numpy as np
import astropy.units as u

from ..importextension import ExtendImports
from ..coordinates_old import Coordinate, CoordinateCollection


class Backend(ExtendImports):
    """
    [This docstring is AI-generated.]
    A base class representing the backend for orbit computation and extraction.

    This class provides a foundation for creating backend classes that perform orbit
    computation and data extraction. It contains abstract and concrete methods that
    need to be implemented in subclasses.

    Attributes:
        None
    """

    def __imports__():
        """
        [This docstring is AI-generated.]
        Placeholder method for specifying extra imports required by subclasses.

        When subclassing this class, you can include additional import statements here.
        These imports will be added to the namespace of the subclass, allowing you to
        use them through attribute access.

        Returns:
            None
        """
        ...

    @abstractmethod
    def _extract_points_from_orbit(orbit: typing.Any,
                                   **kwargs
                                   ) -> np.ndarray:
        """
        [This docstring is AI-generated.]
        Abstract method for extracting points from an orbit.

        This method needs to be implemented by subclasses to extract data points from
        the computed orbit.

        Parameters:
            orbit (typing.Any): The computed orbit.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: An array of data points extracted from the orbit.
        """
        pass

    @abstractmethod
    def _compute_orbit(self,
                       coord: Coordinate,
                       **kwargs):
        """
        [This docstring is AI-generated.]
        Abstract method for computing an orbit for a single coordinate.

        This method needs to be implemented by subclasses to compute an orbit for a
        single coordinate.

        Parameters:
            coord (Coordinate): The coordinate for which to compute the orbit.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        pass

    @abstractmethod
    def _compute_orbits(self,
                        coords: CoordinateCollection,
                        **kwargs):
        """
        [This docstring is AI-generated.]
        Abstract method for computing orbits for multiple coordinates.

        This method needs to be implemented by subclasses to compute orbits for a
        collection of coordinates.

        Parameters:
            coords (CoordinateCollection): The collection of coordinates.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        pass

    def _precompute_namespace_hook(self,
                                   namespace: typing.MutableMapping
                                   ) -> tuple[dict, dict]:
        """
        [This docstring is AI-generated.]
        Hook method for precomputing namespace modifications.

        This method can be overridden by subclasses to precompute modifications to the
        namespace before computation and extraction.

        Parameters:
            namespace (typing.MutableMapping): The namespace containing input parameters.

        Returns:
            tuple[dict, dict]: Two dictionaries containing modifications for computing
                               and extracting orbits respectively.
        """
        return {}, {}

    def get_orbit(self,
                  pot: typing.Any,
                  coord: Coordinate,
                  dt: typing.Union[float, typing.Collection],
                  steps: int,
                  *,
                  pattern_speed: u.Quantity = 0,
                  **kwargs
                  ) -> np.ndarray:
        """
        [This docstring is AI-generated.]
        Get computed orbit for a single coordinate.

        Parameters:
            pot (typing.Any): The potential model.
            coord (Coordinate): The coordinate for which to compute the orbit.
            dt (typing.Union[float, typing.Collection]): Time step(s) for integration.
            steps (int): Number of integration steps.
            pattern_speed (u.Quantity, optional): The pattern speed. Defaults to 0.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: Computed orbit data points.
        """
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbit = self._compute_orbit(coord, **computing_kwargs, **kwargs)
        return self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbits(self,
                    pot: typing.Any,
                    coords: CoordinateCollection,
                    dt: typing.Union[float, typing.Collection],
                    steps: int,
                    *,
                    pattern_speed: u.Quantity = 0,
                    **kwargs
                    ) -> typing.Generator[np.ndarray, None, None]:
        """
        [This docstring is AI-generated.]
        Iterate over computed orbits for multiple coordinates.

        Parameters:
            pot (typing.Any): The potential model.
            coords (CoordinateCollection): The collection of coordinates.
            dt (typing.Union[float, typing.Collection]): Time step(s) for integration.
            steps (int): Number of integration steps.
            pattern_speed (u.Quantity, optional): The pattern speed. Defaults to 0.
            **kwargs: Additional keyword arguments.

        Yields:
            typing.Generator[np.ndarray, None, None]: Generator yielding computed orbit data points.
        """
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            yield self._extract_points_from_orbit(orbit, **extracting_kwargs)

    def iter_orbit_slices(self,
                          pot: typing.Any,
                          coords: CoordinateCollection,
                          dt: typing.Union[float, typing.Collection],
                          *steps: int,
                          pattern_speed: u.Quantity = 0,
                          **kwargs
                          ) -> typing.Generator[tuple[np.ndarray], None, None]:
        """
        [This docstring is AI-generated.]
        Iterate over slices of computed orbits for multiple coordinates.

        Parameters:
            pot (typing.Any): The potential model.
            coords (CoordinateCollection): The collection of coordinates.
            dt (typing.Union[float, typing.Collection]): Time step(s) for integration.
            *steps (int): Steps at which to yield slices.
            pattern_speed (u.Quantity, optional): The pattern speed. Defaults to 0.
            **kwargs: Additional keyword arguments.

        Yields:
            typing.Generator[tuple[np.ndarray], None, None]: Generator yielding tuples of slices of
                computed orbit data points.
        """
        steps = [0] + sorted(steps)
        computing_kwargs, extracting_kwargs = self._precompute_namespace_hook(locals())
        orbits = self._compute_orbits(coords, **computing_kwargs, **kwargs)
        for orbit in orbits:
            points = self._extract_points_from_orbit(orbit, **extracting_kwargs)
            iter_points = iter(points)
            yield (np.array(list(islice(iter_points, s2 - s1))) for s1, s2 in pairwise(steps))
