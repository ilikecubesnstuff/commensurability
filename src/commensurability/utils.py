import inspect
from math import ceil

from collections.abc import Collection, Sequence, Iterator
from itertools import islice

import numpy as np
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
    if isinstance(obj, Sequence) and len(obj) > 0:
        obj = obj[0]
    module = inspect.getmodule(obj)
    if module is None:
        return None
    pkg, *rest = module.__name__.partition('.')
    return pkg


def make_quantity(obj, unit: u.Unit = u.dimensionless_unscaled):
    if isinstance(obj, u.Quantity):
        return obj
    return obj * unit


def make_collection(obj, cls: type = list):
    if not issubclass(cls, Collection):
        raise ValueError('Class provided must subclass collections.abc.Collection')

    # mypy doesn't let me instantiate cls with arguments?
    # look into this later
    if not isinstance(obj, Collection):
        obj = [obj]
    elif isinstance(obj, np.ndarray) and obj.size == 1 and obj.ndim == 0:
        obj = [obj]
    elif len(obj) <= 1:
        obj = [obj]

    if isinstance(obj, u.Quantity):
        return make_collection(obj.value)
    return obj


def make_sequence(obj, cls: type = list):
    if not issubclass(obj, Sequence):
        raise ValueError('Class provided must subclass collections.abc.Sequence')
    if not isinstance(obj, Sequence):
        obj = cls([obj])
    return obj
