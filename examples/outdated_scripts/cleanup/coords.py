

from commensurability.analysis.coordinates import Cylindrical, Cartesian


c = Cylindrical(R=[1, 2, 3], vR=0, vT=1, z=0, vz=0, phi=90)
print(c)
print(c.to(Cartesian))
