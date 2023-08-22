from __future__ import annotations

import numpy as np
import astropy.units as u

from .base import Coordinate


class Cartesian(Coordinate):
    x: u.kpc
    y: u.kpc
    z: u.kpc
    vx: u.km / u.s
    vy: u.km / u.s
    vz: u.km / u.s

    class Transforms:
        def to_cylindrical(self: Cartesian) -> Cylindrical:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            R = np.sqrt(self.x ** 2 + self.y ** 2)
            phi = np.arctan2(self.y, self.x)

            vR = (self.x * self.vx + self.y * self.vy)/R
            vT = (-self.y * self.vx + self.x * self.vy)/R

            return Cylindrical(R=R, vR=vR, vT=vT, z=self.z, vz=self.vz, phi=phi)


class Cylindrical(Coordinate):
    R: u.kpc
    vR: u.km / u.s
    vT: u.km / u.s
    z: u.kpc
    vz: u.km / u.s
    phi: u.deg

    class Transforms:
        def to_cartesian(self: Cylindrical) -> Cartesian:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            x = self.R * np.cos(self.phi)
            y = self.R * np.sin(self.phi)

            vx = self.vR * np.cos(self.phi) - self.vT * np.sin(self.phi)
            vy = self.vT * np.cos(self.phi) + self.vR * np.sin(self.phi)

            return Cartesian(x=x, y=y, z=self.z, vx=vx, vy=vy, vz=self.vz)

        def to_spherical(self: Cylindrical) -> Spherical:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            R = np.sqrt(self.R**2 + self.z**2)
            theta = np.arctan2(self.R, self.z)

            vR = (self.R * self.vR + self.z * self.vz)/R
            v_alt = (self.z * self.vR - self.R * self.vz)/R

            return Spherical(R=R, phi=self.phi, theta=theta, vR=vR, v_alt=v_alt, v_az=self.vT)


class Spherical(Coordinate):
    R: u.kpc
    phi: u.deg
    theta: u.deg
    vR: u.km / u.s
    v_alt: u.km / u.s
    v_az: u.km / u.s

    class Transforms:
        def to_cylindrical(self: Spherical) -> Cylindrical:
            # implemented from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            R = self.R * np.sin(self.theta)
            z = self.R * np.cos(self.theta)

            vR = np.sin(self.theta) * self.vR + np.cos(self.theta) * self.v_alt
            vz = np.cos(self.theta) * self.vR - np.sin(self.theta) * self.v_alt

            return Cylindrical(R=R, phi=self.phi, z=z, vR=vR, vT=self.v_az, vz=vz)
