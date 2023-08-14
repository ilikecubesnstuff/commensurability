import numpy as np
import matplotlib.pyplot as plt


class InteractivePhasePlot:

    def __init__(self, analysis):
        self.analysis = analysis
        self.a1, self.a2 = analysis.axes[:2]
        ax1 = analysis.coords[self.a1].value
        ax2 = analysis.coords[self.a2].value
        MIN1 = np.min(ax1)
        MAX1 = np.max(ax1)
        MIN2 = np.min(ax2)
        MAX2 = np.max(ax2)
        self.extent = (MIN1, MAX1, MIN2, MAX2)
        self.aspect = (MAX1 - MIN1) / (MAX2 - MIN2)
        self.image = analysis.image

    def on_right_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        # NOTE: hardcoded to cylindrical, fix this
        values = {ax: self.analysis.coords[ax][0] for ax in self.analysis.coords.axes}
        values[self.a1] = event.xdata * values[self.a1].unit
        values[self.a2] = event.ydata * values[self.a2].unit
        new_coord = self.analysis.coords.Coordinate(**values)
        print(new_coord)
        points = self.analysis.backend.get_orbit(
            pot=self.analysis.pot,
            coord=new_coord,
            dt=self.analysis.dt,
            steps=self.analysis.steps,
            pattern_speed=self.analysis.pattern_speed
        )
        value = self.analysis.evaluate(points)
        X, Y, Z = points.T

        self.l_orbit.set_data_3d(X, Y, Z)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        Zrange = max(abs(Z))
        XYZrange = max(Xrange, Yrange, Zrange)
        self.ax_orbit.set_xlim([-XYZrange, XYZrange])
        self.ax_orbit.set_ylim([-XYZrange, XYZrange])
        self.ax_orbit.set_zlim([-XYZrange, XYZrange])
        self.ax_orbit.set_title(f'{value = }')

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_left_click(self):
        pass

    def on_scroll(self):
        pass

    def _mpl_button_press_event(self, event):
        if event.inaxes is not self.ax_phase:
            return

        for thing in self.garbage:
            thing.remove()

        if event.button == 1:
            self.on_right_click(event)
        if event.button == 3:
            self.on_left_click(event)

    def _mpl_scroll_event(self):
        pass

    def _mpl_key_press_event(self):
        pass

    def show(self):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122, projection='3d')

        # left plot: phase space
        kwargs = dict(
            origin='lower',
            cmap='inferno',
            vmin=0,
            vmax=1,
            extent=self.extent,
            aspect=self.aspect
        )
        self.im_phase = self.ax_phase.imshow(self.image.T, **kwargs)
        self.dot_phase, = self.ax_phase.plot([self.extent[0]], self.extent[2])

        # right plot: orbit in configuration space
        self.l_orbit, = self.ax_orbit.plot([0], [0], [0], '.k-', linewidth=0.5)
        self.garbage = set()

        # connect methods to figure
        self.connections = []
        self.connections.append(
            self.fig.canvas.mpl_connect('button_press_event', self._mpl_button_press_event)
        )

        plt.show()
