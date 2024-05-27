"""
This module defines custom exceptions for the tessellation package.
These custom exceptions are used to handle specific error cases in
the tessellation package.

It includes the `LowDimensionalityException` class, which is raised
when low-dimensional data is encountered and the tessellation
algorithm cannot proceed.
"""


class LowDimensionalityException(Exception):
    """
    Exception raised when a point collection is less than the minimum supported dimensionality in the tessellation package.
    """

    pass
