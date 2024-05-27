"""
This subpackage contains 6 modules. It implements an evaluation class using
a tessellation and trimming algorithm for commensurability analysis.

The tessellation and trimming algorithm is implemented across the following:

- `base.py` - the main algorithm.
- `dim2.py` - 2D method implementations and normalizations routines.
- `dim3.py` - 3D method implementations and normalization routines.
- `generic.py` - general N-D method implementations and normalization routines.

Package-specific exceptions are defined in `exceptions.py`.

The function used to construct tessellation objects is defined in `constructor.py`.
"""

from .constructor import Tessellation
