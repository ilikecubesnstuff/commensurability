# from collections.abc import Collection

# from commensurability.analysis.coordinates import Coordinate, Cylindrical, Cartesian, CoordinateCollection


# c = Cylindrical(R=[1, 2, 3], vR=0, vT=[1, 2, 3], z=0, vz=0, phi=90)
# print(c)

# def test():
#     yield from c

# for ic in test():
#     print(ic)


# print(a := c.to(Cylindrical))

# x = next(iter(a))
# print(type(x))
# print(isinstance(x, Coordinate))
# print(isinstance(a, Collection))

# c.save('test.hdf5')
# c = Cylindrical.read('test.hdf5')


# from commensurability.analysis import coordinates_old
from commensurability.analysis.coordinates.base import X, Y, Cartesian, Cylindrical


x = X(x=[2, 3, 4], y=[5, 6, 7])
print(x)
print(x.to(Y))


c = Cylindrical(R=[1, 2, 3], vR=0, vT=[1, 2, 3], z=0, vz=0, phi=90)
print(c)
print(c.to(Cartesian))
for ic in c:
    print(ic)