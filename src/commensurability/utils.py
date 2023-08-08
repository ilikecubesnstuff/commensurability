
from itertools import islice
def clump(iterable, size=10):
    while True:
        c = tuple(islice(iterable, size))
        if not c:
            return
        yield c

import astropy.units as u
def make_quantity(obj, unit=u.dimensionless_unscaled):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit