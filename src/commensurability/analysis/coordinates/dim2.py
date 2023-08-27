from __future__ import annotations

import numpy as np
import astropy.units as u

from .base import Coordinate


class Coordinate2D(Coordinate):
    dim = 2


class Cartesian(Coordinate2D):
    """
    [This docstring is AI-generated.]
    Class representing a 2D Cartesian coordinate.

    This class defines a 2D Cartesian coordinate with x and y components, along
    with their associated velocities vx and vy.

    Attributes:
        x (u.kpc): x-component of the coordinate.
        y (u.kpc): y-component of the coordinate.
        vx (u.km / u.s): x-component of the velocity.
        vy (u.km / u.s): y-component of the velocity.
    """

    x: u.kpc
    y: u.kpc
    vx: u.km / u.s
    vy: u.km / u.s

    class Transforms:

        def to_polar(self: Cartesian) -> Polar:
            """
            [This docstring is AI-generated.]
            Convert 2D Cartesian coordinate to 2D polar coordinate.

            This method performs a transformation from 2D Cartesian coordinates to
            2D polar coordinates.

            Returns:
                Polar: Transformed 2D polar coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            r = np.sqrt(self.x ** 2 + self.y ** 2)
            t = np.arctan2(self.y, self.x)

            vr = (self.x * self.vx + self.y * self.vy) / r
            vt = (-self.y * self.vx + self.x * self.vy) / r

            return Polar(r=r, t=t, vr=vr, vt=vt)


class Polar(Coordinate2D):
    """
    [This docstring is AI-generated.]
    Class representing a 2D polar coordinate.

    This class defines a 2D polar coordinate with r and t (theta) components,
    along with their associated velocities vr and vt.

    Attributes:
        r (u.kpc): Radial component of the coordinate.
        t (u.deg): Azimuthal angle component of the coordinate.
        vr (u.km / u.s): Radial velocity component.
        vt (u.km / u.s): Azimuthal velocity component.
    """

    r: u.kpc
    t: u.deg
    vr: u.km / u.s
    vt: u.km / u.s

    class Transforms:

        def to_cartesian(self: Polar) -> Cartesian:
            """
            [This docstring is AI-generated.]
            Convert 2D polar coordinate to 2D Cartesian coordinate.

            This method performs a transformation from 2D polar coordinates to
            2D Cartesian coordinates.

            Returns:
                Cartesian: Transformed 2D Cartesian coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            x = self.r * np.cos(self.t)
            y = self.r * np.sin(self.t)

            vx = self.vr * np.cos(self.t) - self.vt * np.sin(self.t)
            vy = self.vt * np.cos(self.t) + self.vr * np.sin(self.t)

            return Cartesian(x=x, y=y, vx=vx, vy=vy)
