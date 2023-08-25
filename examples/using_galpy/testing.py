# from typing import MutableMapping
# from importlib import import_module

# import ast
# import inspect
# import textwrap


# def __unavailable(e: Exception):
#     class Unavailable:
#         def __init__(self):
#             raise e
#     return Unavailable


# class ExtendImportsMeta(type):

#     def __imports__():
#         pass

#     def __new__(metacls, name: str, bases: tuple[type, ...], namespace: MutableMapping):
#         imports = namespace.pop('__imports__', metacls.__imports__)
#         src = inspect.getsource(imports)
#         *_, body = src.partition('\n')
#         try:
#             exec(textwrap.dedent(body), {}, namespace)
#         except ModuleNotFoundError as e:
#             return __unavailable(e)
#         return super().__new__(metacls, name, bases, namespace)


# class ExtendImports(metaclass=ExtendImportsMeta):
#     pass



# class test(ExtendImports):

#     def __imports__():
#         import numpy
#         import numpy as np
#         from numpy import array
#         from numpy import array as arr
#         from numpy import min as _min, max as _max, std as _std
#         import numpy, numpy, scipy
#         from commensurability.analysis.backends import GalpyBackend
#         import commensurability.analysis.analysis as anal

#     def test(self, x):
#         return x.value + self


# # print(test)
# # print(test.__dict__)
# # print(inspect.getsource(test))
# # tree = ast.parse(inspect.getsource(test))
# # print(ast.dump(tree, indent=4))

# # print(tree.body[0].body)
# x = test()
# print('inst', x)
# print(x.numpy)


from commensurability.analysis.coordinates_old import Coordinate

print(Coordinate.hdf5_serializable)