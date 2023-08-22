# from collections.abc import Collection

# from commensurability.analysis.fileio import Serializer, GenericInheritanceMeta



# class X(metaclass=GenericInheritanceMeta):
#     __type__ = list[Collection]

# class Y(metaclass=GenericInheritanceMeta):
#     __type__ = list[list]

# print(issubclass(Y, X))


# from typing import Union, Any
# from collections.abc import Mapping, Collection


# RUN_SERIALIZER_TESTS = True
# RUN_DESERIALIZER_TESTS = False

# if RUN_SERIALIZER_TESTS:
#     print('SERIALIZER TESTS -------------------------------------------------')
#     from commensurability.analysis.persistence.meta import serializer, Serializer
#     @serializer
#     def test() -> tuple[list[float], dict[str, list[float]]]:
#         return [], {}

#     print(f'{test = }')
#     print(f'{type(test) = }')
#     print(f'{type(type(test)) = }')
#     print(f'{type(type(type(test))) = }')
#     print()
#     print(f'{test() = }')
#     print(f'{type(test()) = }')
#     print()
#     print(f'{issubclass(Serializer[tuple[list[float], dict[str, list[float]]]], Serializer[tuple[list, dict[str, list]]]) = }')
#     print(f'{issubclass(Serializer[tuple[list, dict[str, list]]], Serializer[tuple[Collection, Mapping[str, Collection]]]) = }')
#     print(f'{issubclass(Serializer[tuple[list, dict[str, list]]], Serializer[tuple[Collection, Mapping[str, float]]]) = }')
#     print(f'{issubclass(Serializer[tuple[list, dict[str, list]]], Serializer[tuple[tuple, Mapping[str, float]]]) = }')
#     print(f'{issubclass(Serializer[tuple], Serializer[Union[tuple, int]]) = }')
#     print(f'{issubclass(Serializer[Any], Serializer[Union[tuple, int]]) = }')
#     print(f'{issubclass(Serializer[Union[tuple, int]], Serializer[Any]) = }')
#     print()

#     def test() -> Any:
#         pass
#     print(f'{Serializer = }')
#     print(f'{type(Serializer) = }')
#     print(f'{type(type(Serializer)) = }')
#     print(f'{Serializer(test) = }')
#     print(f'{type(Serializer)() = }')
#     print(f'{type(type(Serializer))() = }')



# if RUN_DESERIALIZER_TESTS:
#     print('DESERIALIZER TESTS -------------------------------------------------')
#     from commensurability.analysis.persistence.meta import deserializer, Deserializer
#     @deserializer
#     def test(arr: list, /, name: str, alias: list[str] | None):
#         pass

#     print(f'{test = }')
#     print(f'{type(test) = }')
#     print(f'{type(type(test)) = }')
#     print(f'{type(type(type(test))) = }')
#     print()
#     print(f'{test() = }')
#     print(f'{type(test()) = }')



# import typing
# from commensurability.analysis.persistence.meta import serializer, recursive_subtype_check


# @serializer
# def test1() -> tuple[list[float], dict[str, list[float]]]:
#     return [], {}
# test = test1

# @serializer
# def test2() -> tuple[list, dict[str, list]]:
#     return [], {}

# @serializer
# def test3() -> tuple[list, dict]:
#     return [], {}

# @serializer
# def test4() -> tuple:
#     return [], {}

# @serializer
# def test5() -> typing.Any:
#     return [], {}


# from itertools import product
# fs = [test1, test2, test3, test4, test5]
# for f1, f2 in product(fs, fs):
#     print(f'{f1.func.__name__}:{f2.func.__name__} - {issubclass(type(f1), type(f2))}')

# print(f'{test = }')
# print(f'{type(test) = }')
# print(f'{type(type(test)) = }')
# print(f'{type(type(type(test))) = }')





import typing
from commensurability.analysis.persistence.serialization import serializer, deserializer

@serializer.create
def s1() -> tuple[list[float], dict[str, list[float]]]:
    return [], {}
test = s1

@serializer.create
def s2() -> tuple[list, dict[str, list]]:
    return [], {}

@deserializer.create
def d1(a1: list[float], a2: dict[str, list[float]]):
    pass

@deserializer.create
def d2(a1, a2: dict[str, list]):
    pass


print(s1.__name__)
print(s1())
print(s1)
print(type(s1))
print(type(type(s1)))
print(type(type(type(s1))))
print(s2)
print(d1)
print(d2)
print(f'{issubclass(type(d2), type(d1)) = }')
print(f'{issubclass(type(d1), type(d2)) = }')


# @serializer.create
# def test3() -> tuple[list, dict]:
#     return [], {}

# @serializer.create
# def test4() -> tuple:
#     return [], {}

# @serializer.create
# def test5() -> typing.Any:
#     return [], {}

# fs = [test1, test2, test3, test4, test5]

# for f in fs:
#     print(f.__name__, f)

# from itertools import product
# for f1, f2 in product(fs, fs):
#     print(f'{f1.__name__}:{f2.__name__} - {issubclass(type(f1), type(f2))}')

# print(f'{test = }')
# print(f'{type(test) = }')
# print(f'{type(type(test)) = }')
# print(f'{type(type(type(test))) = }')

# print(f'{test() = }')











# from commensurability.analysis.persistence.meta import *

# print(vars(Test))
# print(vars(Test()))