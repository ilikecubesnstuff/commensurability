"""
This module defines abstract base classes for evaluation classes to be
defined in subpackages. Evaluation classes must implement a "measure"
property and a "plot" method to work with the analysis classes.
"""

from abc import abstractmethod

import astropy.coordinates as c


class Evaluation:
    """
    Class representing an evaluation of an orbit's commensurability.

    This class defines methods for evaluating an orbit and generating plots.
    """

    def __init__(self, orbit: c.SkyCoord):
        """
        Initialize Evaluation object.

        Args:
            orbit: Orbit to be evaluated.
        """
        self.orbit = orbit

    def __reduce__(self):
        return self.__class__, (self.orbit,)

    @property
    @abstractmethod
    def measure(self) -> float:
        """
        Get the evaluation value.

        Returns:
            Measure of the evaluation.
        """
        pass

    @abstractmethod
    def plot(self):
        """
        Create a plot of the evaluation.
        """
        pass
