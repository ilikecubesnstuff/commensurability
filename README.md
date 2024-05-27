# commensurability

[![PyPI - Version](https://img.shields.io/pypi/v/commensurability)](https://pypi.org/project/commensurability/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/commensurability)](https://pypi.org/project/commensurability/)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A Python package for performing analysis on orbit commensurabilities.

This package uses [`pidgey`](https://github.com/ilikecubesnstuff/pidgey) as its orbit integration backend.

## Installation

Install this package via `pip`:

```
python -m pip install commensurability
```

## Usage

See the [documentation](https://commensurability.readthedocs.io/en/latest/) page.

This package is to be used along with one of the galactic dynamics packages [`agama`](https://github.com/GalacticDynamics-Oxford/Agama), [`gala`](https://gala-astro.readthedocs.io/en/latest/), or [`galpy`](https://docs.galpy.org/en/latest/).
There are scripts for each under the `examples` folder that can be run to test whether everything is working correctly.
