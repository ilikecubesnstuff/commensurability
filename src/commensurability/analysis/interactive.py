

import matplotlib.pyplot as plt


# TODO: needs implementation
# see 'interactive.py' examples: examples/outdated_scripts/using_galpy/*/interactive.py


class InteractivePhasePlot:

    def __init__(self, pot):
        self.image = None  # data array
        pass

    @classmethod
    def from_hdf5(self, filename):
        pass

    def on_left_click(self):
        pass

    def on_right_click(self):
        pass

    def on_scroll(self):
        pass

    def _mpl_button_press_event(self):
        pass

    def _mpl_scroll_event(self):
        pass

    def _mpl_key_press_event(self):
        pass

    def show(self):
        fig, (ax_phase, ax_orbit) = plt.subplots(1, 2, figsize=(12, 5))

        # left plot: phase space
        # TODO: implement this

        # right plot: orbit in configuration space
        # TODO: implement this

        # connect methods to figure
        self.connections = []
