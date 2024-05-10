"""
This package contains 6 modules.

The tessellation and trimming algorithm is implemented across the following:

- `base.py` - the main algorithm.
- `dim2.py` - 2D method implementations and normalizations routines.
- `dim3.py` - 3D method implementations and normalization routines.
- `generic.py` - general N-D method implementations and normalization routines.

Package-specific exceptions are defined in `exceptions.py`.

The function used to construct tessellation objects is defined in `constructor.py`.
"""

from importlib.metadata import version as _version

__version__ = _version("orbit-tessellation")

from .constructor import Tessellation
