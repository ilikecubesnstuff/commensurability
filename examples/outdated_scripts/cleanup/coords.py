from collections.abc import Collection

from commensurability.analysis.coordinates import Coordinate, Cylindrical, Cartesian, CoordinateCollection


c = Cylindrical(R=[1, 2, 3], vR=0, vT=[1, 2, 3], z=0, vz=0, phi=90)
print(c)

def test():
    yield from c

for ic in test():
    print(ic)


print(a := c.to(Cylindrical))

x = next(iter(a))
print(type(x))
print(isinstance(x, Coordinate))
print(isinstance(a, Collection))