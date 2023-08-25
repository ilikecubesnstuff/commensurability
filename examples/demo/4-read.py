# no other imports required

# all the code is taken care of inside the library

# currently, a FileIO object and a TessellationAnalysis
# object is all that is required


# package imports
from commensurability.analysis import TessellationAnalysis
from commensurability.analysis.fileio import FileIO

# read in analysis object
f = FileIO(f'demo.hdf5')
tanal = f.read(TessellationAnalysis)

# scroll & click to explore the phase space
tanal.launch_interactive_plot()