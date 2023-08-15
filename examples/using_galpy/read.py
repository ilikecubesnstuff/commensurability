

# import h5py

# with h5py.File('mw_bar_10.hdf5') as f:
#     print(f.keys())
#     print(f['TessellationAnalysis'])
#     print(f['TessellationAnalysis'].attrs.keys())


from commensurability.analysis import TessellationAnalysis
from commensurability.analysis.fileio import FileIO

SIZE = 2
FRAMES = 5
f = FileIO(f'mw_bar_{SIZE}_{FRAMES}.hdf5')
tanal = f.read(TessellationAnalysis)
tanal.launch_interactive_plot()


