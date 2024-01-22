# package imports
from commensurability import TessellationAnalysis2D

# read in analysis object
tanal = TessellationAnalysis2D.read_from_hdf5("5-data.hdf5")

# scroll & click to explore the phase space
tanal.launch_interactive_plot("x", "vy")
