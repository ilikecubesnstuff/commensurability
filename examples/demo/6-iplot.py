# package imports
from commensurability import TessellationAnalysis

# read in analysis object
tanal = TessellationAnalysis.read_from_hdf5("6-iplot-demo.hdf5")

# scroll & click to explore the phase space
tanal.launch_interactive_plot("x", "vy")
