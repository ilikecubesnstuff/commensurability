from __future__ import annotations

import numpy as np
import astropy.units as u

from .base import Coordinate


class Coordinate3D(Coordinate):
    pass


class Cartesian(Coordinate3D):
    """
    [This docstring is AI-generated.][Modified]
    Class representing a Cartesian coordinate.

    This class defines a Cartesian coordinate in a 3D space with x, y, and z components,
    along with their associated velocities vx, vy, and vz.

    Attributes:
        x (u.kpc): x-component of the position.
        y (u.kpc): y-component of the position.
        z (u.kpc): z-component of the position.
        vx (u.km / u.s): x-component of the velocity.
        vy (u.km / u.s): y-component of the velocity.
        vz (u.km / u.s): z-component of the velocity
    """

    x: u.kpc
    y: u.kpc
    z: u.kpc
    vx: u.km / u.s
    vy: u.km / u.s
    vz: u.km / u.s

    class Transforms:

        def to_cylindrical(self: Cartesian) -> Cylindrical:
            """
            [This docstring is AI-generated.]
            Convert Cartesian coordinate to cylindrical coordinate.

            This method performs a transformation from Cartesian coordinates to
            cylindrical coordinates.

            Returns:
                Cylindrical: Transformed cylindrical coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            R = np.sqrt(self.x ** 2 + self.y ** 2)
            phi = np.arctan2(self.y, self.x)

            vR = (self.x * self.vx + self.y * self.vy) / R
            vT = (-self.y * self.vx + self.x * self.vy) / R

            return Cylindrical(R=R, vR=vR, vT=vT, z=self.z, vz=self.vz, phi=phi)


class Cylindrical(Coordinate3D):
    """
    [This docstring is AI-generated.]
    Class representing a cylindrical coordinate.

    This class defines a cylindrical coordinate in a 3D space with R, phi, and z
    components, along with their associated velocities vR, vT, and vz.

    Attributes:
        R (u.kpc): Radial component of the coordinate.
        phi (u.deg): Azimuthal angle component of the coordinate.
        z (u.kpc): z-component of the coordinate.
        vR (u.km / u.s): Radial velocity component.
        vT (u.km / u.s): Azimuthal velocity component.
        vz (u.km / u.s): z-component of the velocity.
    """

    R: u.kpc
    vR: u.km / u.s
    vT: u.km / u.s
    z: u.kpc
    vz: u.km / u.s
    phi: u.deg

    class Transforms:

        def to_cartesian(self: Cylindrical) -> Cartesian:
            """
            [This docstring is AI-generated.]
            Convert cylindrical coordinate to Cartesian coordinate.

            This method performs a transformation from cylindrical coordinates to
            Cartesian coordinates.

            Returns:
                Cartesian: Transformed Cartesian coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            x = self.R * np.cos(self.phi)
            y = self.R * np.sin(self.phi)

            vx = self.vR * np.cos(self.phi) - self.vT * np.sin(self.phi)
            vy = self.vT * np.cos(self.phi) + self.vR * np.sin(self.phi)

            return Cartesian(x=x, y=y, z=self.z, vx=vx, vy=vy, vz=self.vz)

        def to_spherical(self: Cylindrical) -> Spherical:
            """
            [This docstring is AI-generated.]
            Convert cylindrical coordinate to spherical coordinate.

            This method performs a transformation from cylindrical coordinates to
            spherical coordinates.

            Returns:
                Spherical: Transformed spherical coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            R = np.sqrt(self.R ** 2 + self.z ** 2)
            theta = np.arctan2(self.R, self.z)

            vR = (self.R * self.vR + self.z * self.vz) / R
            v_alt = (self.z * self.vR - self.R * self.vz) / R

            return Spherical(R=R, phi=self.phi, theta=theta, vR=vR, v_alt=v_alt, v_az=self.vT)


class Spherical(Coordinate3D):
    """
    [This docstring is AI-generated.]
    Class representing a spherical coordinate.

    This class defines a spherical coordinate in a 3D space with R, phi, and theta
    components, along with their associated velocities vR, v_alt, and v_az.

    Attributes:
        R (u.kpc): Radial component of the coordinate.
        phi (u.deg): Azimuthal angle component of the coordinate.
        theta (u.deg): Polar angle component of the coordinate.
        vR (u.km / u.s): Radial velocity component.
        v_alt (u.km / u.s): Alternative velocity component.
        v_az (u.km / u.s): Azimuthal velocity component.
    """
    # alternative velocity?? I'm not sure what the proper term for this is, actually
    # but alternative velocity cannot be correct  (TODO)

    R: u.kpc
    phi: u.deg
    theta: u.deg
    vR: u.km / u.s
    v_alt: u.km / u.s
    v_az: u.km / u.s

    class Transforms:

        def to_cylindrical(self: Spherical) -> Cylindrical:
            """
            [This docstring is AI-generated.]
            Convert spherical coordinate to cylindrical coordinate.

            This method performs a transformation from spherical coordinates to
            cylindrical coordinates.

            Returns:
                Cylindrical: Transformed cylindrical coordinate.
            """
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates

            R = self.R * np.sin(self.theta)
            z = self.R * np.cos(self.theta)

            vR = np.sin(self.theta) * self.vR + np.cos(self.theta) * self.v_alt
            vz = np.cos(self.theta) * self.vR - np.sin(self.theta) * self.v_alt

            return Cylindrical(R=R, phi=self.phi, z=z, vR=vR, vT=self.v_az, vz=vz)
