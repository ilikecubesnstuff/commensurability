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
        def to_polar(self: Cartesian) -> Polar:
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            r = np.sqrt(self.x ** 2 + self.y ** 2)
            t = np.arctan2(self.y, self.x)

            vr = (self.x * self.vx + self.y * self.vy)/r
            vt = (-self.y * self.vx + self.x * self.vy)/r

            return Polar(r=r, t=t, vr=vr, vt=vt)


class Polar(Coordinate):
    r: u.kpc
    t: u.deg
    vr: u.km / u.s
    vt: u.km / u.s

    class Transforms:
        def to_cartesian(self: Polar) -> Cartesian:
            # adapted from https://en.wikipedia.org/wiki/Del_in_cylindrical_and_spherical_coordinates
            x = self.r * np.cos(self.t)
            y = self.r * np.sin(self.t)

            vx = self.vr * np.cos(self.t) - self.vt * np.sin(self.t)
            vy = self.vt * np.cos(self.t) + self.vr * np.sin(self.t)

            return Cartesian(x=x, y=y, vx=vx, vy=vy)