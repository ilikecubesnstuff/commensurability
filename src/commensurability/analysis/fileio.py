from __future__ import annotations
from typing import Any
import h5py


class WriteError(Exception):
    pass


class FileIO:

    def __init__(self, filename):
        self.filename = filename

    def save(self, obj: Any, **kwargs):
        if not hasattr(obj, '__save__'):
            raise TypeError(f'{obj} cannot be saved with {self.__class__.__name__}')
        try:
            attrs, data = obj.__save__(**kwargs)
            # print(data, attrs)
            with h5py.File(self.filename, 'w') as f:
                dset = f.create_dataset(obj.__class__.__name__, data=data)
                # print(data)
                for attr, value in attrs.items():
                    dset.attrs[attr] = value
        except Exception as e:
            raise WriteError(f'Unable to save {obj} to {self.filename}: {e}')

    def read(self, *cls: type):
        if not all(hasattr(cl, '__read__') for cl in cls):
            raise TypeError(f'{cls} cannot be read with {self.__class__.__name__}')
        try:
            objs = []
            with h5py.File(self.filename) as f:
                for cl in cls:
                    obj = cl.__read__(f[cl.__name__])
                    objs.append(obj)
            if len(objs) == 1:
                return objs[0]
            return objs
        except Exception as e:
            raise e
            raise WriteError(f'Unable to read {cl} from {self.filename}: {e}')
