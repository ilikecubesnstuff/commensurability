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
    # it seems as though astropy coordinates discard
    # velocity data by default when combining coordinates
    # i'm not sure of a better approach for this step
    if isinstance(coords, c.SkyCoord):
        return coords
    for coord in coords:
        coord.representation_type = "cartesian"
    data = [(coord.x, coord.y, coord.z, coord.v_x, coord.v_y, coord.v_z) for coord in coords]
    x, y, z, v_x, v_y, v_z = list(zip(*data))
    return c.SkyCoord(
        x=x,
        y=y,
        z=z,
        v_x=v_x,
        v_y=v_y,
        v_z=v_z,
        frame="galactocentric",
        representation_type="cartesian",
    )
