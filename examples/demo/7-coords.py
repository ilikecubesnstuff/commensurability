from __future__ import annotations

import numpy as np
import astropy.units as u

from commensurability.analysis.coordinates import Coordinate, Cartesian


# defining a new coordinate system
class ParabolicCylindrical(Coordinate):
    s: u.kpc ** 0.5
    t: u.kpc ** 0.5
    z: u.kpc
    vs: u.km / u.s
    vt: u.km / u.s
    vz: u.km / u.s

    class Transforms:

        def to_cartesian(self: ParabolicCylindrical) -> Cartesian:
            # adapted from https://en.wikipedia.org/wiki/Elliptic_coordinate_system
            x = self.s * self.t
            y = 0.5 * (self.s**2 - self.t**2)
            
            d = self.s**2 + self.t**2
            vx = (self.s * self.vt + self.t * self.vs) / d
            vy = (self.t * self.vt - self.s * self.vs) / d

            return Cartesian(x=x, y=y, z=self.z, vx=vx, vy=vy, vz=self.vz)


# using this coordinate system
coords = ParabolicCylindrical(s=[1, 2, 3], t=[4, 5], z=0, vs=1, vt=0, vz=[-1, 1])
for coord in coords:
    print(coord)
    print(coord._transform_to(Cartesian), end='\n\n')
