from importlib.metadata import version as _version

__version__ = _version("orbit-tessellation")

# import user-facing analysis classes
from .analysis import TessellationAnalysis, TessellationAnalysis2D
