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

``commensurability`` can work on pre-computed files of integrated orbits and
therefore does not strictly require any orbit integration backend to be
installed. This is why ``commensurability`` does not install any such library.
However, if you are not working with a pre-computed file and need
``commensurability`` to integrate a grid of orbits you will need to have an
orbit integration library installed (e.g. `agama`, `gala`, or `galpy`). Chances
are you probably do! ``commensurability`` automatically installs and uses
[``pidgey``](https://pypi.org/project/pidgey/) to support many different
libraries. Check out [``pidgey``](https://pypi.org/project/pidgey/) to see
whether your preferred library is supported, or how to register it with
``pidgey`` if it isn't.
