from commensurability import TessellationAnalysis

SIZE = 5
FRAMES = 5
tanal = TessellationAnalysis.read_from_hdf5(f"examples/using_galpy/mw_bar_{SIZE}_{FRAMES}.hdf5")
tanal.launch_interactive_plot("x", "vy")
