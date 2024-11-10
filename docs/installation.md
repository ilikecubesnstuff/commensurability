# Installation

The preferred installation method is via `pip` from [PyPI](installation.md#from-pypi).

## From PyPI

This package is available on [PyPI](https://pypi.org/project/commensurability/). Install the package via `pip`:

```
python -m pip install commensurability
```

## From Source

Clone the GitHub repository, and install the package via `pip`:

```
git clone https://github.com/ilikecubesnstuff/commensurability.git
cd commensurability
pip install .
```

## Orbit Integration Backends

`commensurability` can work on pre-computed files of integrated orbits and therefore does not strictly require any orbit integration backend to be installed.
This is why `commensurability` does not install any such library.
However, if you are not working with a pre-computed file and need `commensurability` to integrate a grid of orbits you will need to have an orbit integration library installed (e.g. `agama`, `gala`, or `galpy`) that is supported by [`pidgey`](https://pypi.org/project/pidgey/).
[`pidgey`](https://pypi.org/project/pidgey/) states:

> **To use `pidgey`, you require one of the following galactic dynamics libraries installed.**
> 
> | Package | Installation Instructions |
> | ------- | ------------------------- |
> | [`agama`](https://github.com/GalacticDynamics-Oxford/Agama)* | [https://github.com/GalacticDynamics-Oxford/Agama/blob/master/INSTALL](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/INSTALL) |
> | [`gala`](https://github.com/adrn/gala)                       | [https://gala.adrian.pw/en/latest/install.html](https://gala.adrian.pw/en/latest/install.html) |
> | [`galpy`](https://github.com/jobovy/galpy)                   | [https://docs.galpy.org/en/stable/installation.html](https://docs.galpy.org/en/stable/installation.html) |
> 
> ***Note**: Currently, `pidgey` supports [this version of `agama`](https://github.com/GalacticDynamics-Oxford/Agama/tree/0c5993d1c631d9a9e8f48213f919e09bfd629639) (commit hash [0c5993d](https://github.com/GalacticDynamics-Oxford/Agama/tree/0c5993d1c631d9a9e8f48213f919e09bfd629639)).
> `agama` requires WSL on Windows, as well as a C++ compiler.
> After you clone the repository, you may require running an explicit `python setup.py install --user` - this installation pattern is only supported for Python versions <=3.11.

`commensurability` depends on [`pidgey`](https://pypi.org/project/pidgey/) to support many different orbit integration backends.
Check out [`pidgey`](https://pypi.org/project/pidgey/) to see whether your preferred library is supported, or how to register it with `pidgey` if it isn't.
