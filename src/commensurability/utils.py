from collections.abc import Collection, Sequence
from itertools import islice

import astropy.units as u


def clump(iterable, size=10):
    while True:
        c = tuple(islice(iterable, size))
        if not c:
            return
        yield c


def make_quantity(obj, unit: u.Unit=u.dimensionless_unscaled):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit


def make_collection(obj, cls: Collection=list):
    if not issubclass(cls, Collection):
        raise ValueError('Class provided must subclass collections.abc.Collection')
    if not isinstance(obj, Collection):
        obj = cls([obj])
    return obj

def make_sequence(obj, cls: Sequence=list):
    if not issubclass(obj, Sequence):
        raise ValueError('Class provided must subclass collections.abc.Sequence')
    if not isinstance(obj, Sequence):
        obj = cls([obj])
    return obj