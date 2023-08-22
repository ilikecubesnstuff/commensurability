from typing import MutableMapping

import inspect
import textwrap


def _unavailable(e: Exception):
    class Unavailable:
        def __init__(self):
            raise e
    return Unavailable


class ExtendImportsMeta(type):

    def __imports__():
        pass

    def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
        imports = namespace.pop('__imports__', metacls.__imports__)
        src = inspect.getsource(imports)
        *_, body = src.partition('\n')
        try:
            exec(textwrap.dedent(body), {}, namespace)
        except ModuleNotFoundError as e:
            return _unavailable(e)
        return super().__new__(metacls, name, bases, namespace)


class ExtendImports(metaclass=ExtendImportsMeta):
    pass
