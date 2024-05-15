"""
This package contains 4 modules and 1 subpackage.

The analysis, evaluation, and interactive modules define base classes for
their relevant purposes. The analysis module in particular also defines
user-facing classes for 2D and 3D commensurability analysis using the
tessellation subpackage.

Utility functions are defined in `utils.py`.
"""

from importlib.metadata import version as _version

__version__ = _version("commensurability")

# import user-facing analysis classes
from .analysis import TessellationAnalysis, TessellationAnalysis2D
