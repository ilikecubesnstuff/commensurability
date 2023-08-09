from itertools import islice

import numpy as np

from commensurability.tessellation import Tessellation

import h5py



def random_ic(**kwargs):
    pass












def eval_cls(cls, **kwargs):
    return lambda x: cls(x, **kwargs)

def evaluate_phase_space(points_set, _eval=eval_cls(Tessellation, trim=10), chunksize=None):
    while True:
        chunk = []
        for points in slice(points_set, 10):
            eval_obj = _eval(points)
            chunk.append(eval_obj.measure)
        yield chunk


def hdf_format(index, array):
    ic = array[0]
    pass

def write_to_hdf5(filename, array_gen, keyname='data_set', delimiter='_'):
    keyname = lambda n: f'{keyname}{delimiter}{n}'
    with h5py.File(filename, 'w-') as f:
        for i, array in enumerate(array_gen):
            f[keyname(i)] = array


def display_phase_space(filename):
    with h5py.File(filename) as f:
        pass




