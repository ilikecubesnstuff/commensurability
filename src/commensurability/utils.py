import inspect
from math import ceil

from collections.abc import Collection, Sequence, Iterator
from itertools import islice

import astropy.units as u


class clump(Iterator):

    def __init__(self, iterable, clumpsize):
        self.iterable = iterable
        self.it = iter(iterable)
        self.size = clumpsize

    def __len__(self):
        return ceil(len(self.iterable)/self.size)

    def __next__(self):
        c = tuple(islice(self.it, self.size))
        if not c:
            raise StopIteration()
        return c


def get_top_level_package(obj):
    obj = make_collection(obj)[0]
    module = inspect.getmodule(obj)
    pkg, *rest = module.__name__.partition('.')
    return pkg


def make_quantity(obj, unit: u.Unit = u.dimensionless_unscaled):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit


def make_collection(obj, cls: Collection = list):
    if not issubclass(cls, Collection):
        raise ValueError('Class provided must subclass collections.abc.Collection')
    if not isinstance(obj, Collection):
        obj = cls([obj])
    if isinstance(obj, u.Quantity):
        return make_collection(obj.value)
    return obj


def make_sequence(obj, cls: Sequence = list):
    if not issubclass(obj, Sequence):
        raise ValueError('Class provided must subclass collections.abc.Sequence')
    if not isinstance(obj, Sequence):
        obj = cls([obj])
    return obj
