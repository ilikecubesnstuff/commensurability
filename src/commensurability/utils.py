"""
This module defines utility functions for the analysis classes.
"""

from typing import Any

import astropy.coordinates as c
import astropy.units as u


def make_quantity(obj: Any, unit: u.Unit) -> u.Quantity:
    """
    Convert object to a Quantity with specified unit.

    Args:
        obj: Object to convert.
        unit (astropy.units.Unit): Unit to convert to.

    Returns:
        Quantity with specified unit.
    """
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit


def collapse_coords(coords: Any) -> c.SkyCoord:
    """
    Collapse coordinates into a single SkyCoord object.

    Args:
        coords: List of coordinates to collapse.

    Returns:
        Collapsed SkyCoord object.
    """
    if isinstance(coords, c.SkyCoord):
        return coords
    return c.concatenate(coords)
