# commensurability

[![DOI](https://joss.theoj.org/papers/10.21105/joss.07009/status.svg)](https://doi.org/10.21105/joss.07009)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15350426.svg)](https://doi.org/10.5281/zenodo.15350426)
\
[![Coverage Status](https://coveralls.io/repos/github/ilikecubesnstuff/commensurability/badge.svg?branch=main)](https://coveralls.io/github/ilikecubesnstuff/commensurability?branch=main)
[![tests](https://github.com/ilikecubesnstuff/commensurability/actions/workflows/tests.yml/badge.svg)](https://github.com/ilikecubesnstuff/commensurability/actions/workflows/tests.yml)
[![Read The Docs Status](https://readthedocs.org/projects/commensurability/badge/?version=latest&style=flat)](https://commensurability.readthedocs.io/en/stable/)
[![doctests](https://github.com/ilikecubesnstuff/commensurability/actions/workflows/doctests.yml/badge.svg)](https://github.com/ilikecubesnstuff/commensurability/actions/workflows/doctests.yml)
\
[![PyPI - Version](https://img.shields.io/pypi/v/commensurability)](https://pypi.org/project/commensurability/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/commensurability)](https://pypi.org/project/commensurability/)
[![PyPI - License](https://img.shields.io/pypi/l/commensurability)](https://github.com/ilikecubesnstuff/commensurability/blob/main/LICENSE)
\
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

## Contributing

If you wish to contribute to ``commensurability``, please fork the repository and create a [pull request](https://github.com/ilikecubesnstuff/commensurability/pulls).

If you wish to report bugs, request features or suggest other ideas, please open an [issue](https://github.com/ilikecubesnstuff/commensurability/issues).

For more information, see [contributing](https://commensurability.readthedocs.io/en/latest/contributing/) in the documentation.
