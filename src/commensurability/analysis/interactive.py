from abc import abstractmethod

import numpy as np
import matplotlib.pyplot as plt


class InteractivePlotBase:

    def __init__(self, analysis, x_axis, y_axis):
        self.analysis = analysis
        self.x_axis = x_axis
        self.x_unit = analysis.coords[x_axis].unit
        self.y_axis = y_axis
        self.y_unit = analysis.coords[y_axis].unit

        self.axes = [ax for ax in analysis.axes if ax not in [x_axis, y_axis]]
        self.indices = {ax: 0 for ax in self.axes}
        self.coordinates = {ax: analysis.coords[ax] for ax in analysis.axes}  # TODO: adapt for non-coordinate variables
        self.image = analysis.image
        self.current = self.axes[0] if self.axes else None

        XMIN = np.min(self.coordinates[x_axis]).value
        XMAX = np.max(self.coordinates[x_axis]).value
        YMIN = np.min(self.coordinates[y_axis]).value
        YMAX = np.max(self.coordinates[y_axis]).value
        self.extent = (XMIN, XMAX, YMIN, YMAX)
        self.aspect = (XMAX - XMIN) / (YMAX - YMIN)

    def on_right_click(self, event):
        print('Left-click not implemented yet!')

    def on_left_click(self, event):
        print('Left-click not implemented yet!')

    def on_scroll(self, event):
        if not self.current:
            return

        new = self.indices[self.current] + int(event.step)
        # clip the value inside the valid index range
        self.indices[self.current] = max(0, min(self.analysis.coords[self.current].size - 1, new))

        info = ', '.join(f'{ax}={self.coordinates[ax][index]}' for ax, index in self.indices.items())
        self.ax_phase.set_title(info)
        self.im_phase.set_data(self.image[(..., *self.indices.values())].T)

        # reset the rest
        self.dot_phase.set_xdata([self.extent[0]])
        self.dot_phase.set_ydata([self.extent[2]])
        self.l_orbit.set_xdata([0])
        self.l_orbit.set_ydata([0])

        # udpate figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_keypress(self, event):
        print('Key press not implemented yet!')
        # TODO: explore alternate axes (in the case of 4+ dimensional data)


    def _mpl_button_press_event(self, event):
        if event.inaxes is not self.ax_phase:
            return

        for thing in self.garbage:
            thing.remove()

        if event.button == 1:
            self.on_left_click(event)
        if event.button == 3:
            self.on_right_click(event)

    def _mpl_scroll_event(self, event):
        if event.inaxes is not self.ax_phase:
            return

        for thing in self.garbage:
            thing.remove()
        
        self.on_scroll(event)

    def _mpl_key_press_event(self, event):
        self.on_keypress(event)
    
    def _add_connections(self):
        self.connections = []
        self.connections.append(
            self.fig.canvas.mpl_connect('button_press_event', self._mpl_button_press_event)
        )
        self.connections.append(
            self.fig.canvas.mpl_connect('scroll_event', self._mpl_scroll_event)
        )
        self.connections.append(
            self.fig.canvas.mpl_connect('key_press_event', self._mpl_key_press_event)
        )

    def show(self, **imshow_kwargs):
        self.plot_axes(**imshow_kwargs)
        self.garbage = set()

        # connect methods to figure
        self._add_connections()
        plt.show()
    
    @abstractmethod
    def plot_axes(self, **imshow_kwargs):
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
        kwargs.update(**imshow_kwargs)
        self.im_phase = self.ax_phase.imshow(self.image[(..., *self.indices.values())].T, **kwargs)
        self.dot_phase, = self.ax_phase.plot([self.extent[0]], self.extent[2])

        # right plot: orbit in configuration space
        self.l_orbit, = self.ax_orbit.plot([0], [0], [0], '.k-', linewidth=0.5)
    


class InteractivePlot2D(InteractivePlotBase):

    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        # NOTE: needs testing
        values = {ax: self.analysis.coords[ax][0] for ax in self.analysis.coords.axes}
        for ax, index in self.indices.items():
            values[ax] = self.coordinates[ax][index]
        values[self.x_axis] = event.xdata * self.x_unit
        values[self.y_axis] = event.ydata * self.y_unit
        print(values)
        coord = self.analysis.coords.__class__(**values)

        points = self.analysis.backend.get_orbit(
            pot=self.analysis.potential,
            coord=coord,
            dt=self.analysis.dt,
            steps=self.analysis.n,
            pattern_speed=self.analysis.pattern_speed
        )
        value = self.analysis.__eval__(points)

        # for 2D plot
        X, Y = points.T
        self.l_orbit.set_data(X, Y)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        XYrange = max(Xrange, Yrange)
        self.ax_orbit.set_xlim([-XYrange, XYrange])
        self.ax_orbit.set_ylim([-XYrange, XYrange])

        self.ax_orbit.set_title(f'{value = }')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_right_click(self, event):
        print('Right-click not implemented yet!')
        # TODO: plot orbit with tessellation on right plot

    def plot_axes(self, **imshow_kwargs):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122)

        # left plot: phase space
        kwargs = dict(
            origin='lower',
            cmap='inferno',
            vmin=0,
            vmax=1,
            extent=self.extent,
            aspect=self.aspect
        )
        kwargs.update(**imshow_kwargs)
        self.im_phase = self.ax_phase.imshow(self.image[(..., *self.indices.values())].T, **kwargs)
        self.dot_phase, = self.ax_phase.plot([self.extent[0]], self.extent[2])

        # right plot: orbit in configuration space
        self.l_orbit, = self.ax_orbit.plot([0], [0], '.k-', linewidth=0.5)



class InteractivePlot3D(InteractivePlotBase):

    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        # NOTE: needs testing
        values = {ax: self.analysis.coords[ax][0] for ax in self.analysis.coords.axes}
        for ax, index in self.indices.items():
            values[ax] = self.coordinates[ax][index]
        values[self.x_axis] = event.xdata * self.x_unit
        values[self.y_axis] = event.ydata * self.y_unit
        coord = self.analysis.coords.__class__(**values)

        points = self.analysis.backend.get_orbit(
            pot=self.analysis.potential,
            coord=coord,
            dt=self.analysis.dt,
            steps=self.analysis.n,
            pattern_speed=self.analysis.pattern_speed
        )
        value = self.analysis.__eval__(points)

        # for 3D plot
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

    def on_right_click(self, event):
        print('Right-click not implemented yet!')
        # TODO: plot orbit with tessellation on right plot

    def plot_axes(self, **imshow_kwargs):
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
        kwargs.update(**imshow_kwargs)
        self.im_phase = self.ax_phase.imshow(self.image[(..., *self.indices.values())].T, **kwargs)
        self.dot_phase, = self.ax_phase.plot([self.extent[0]], self.extent[2])

        # right plot: orbit in configuration space
        self.l_orbit, = self.ax_orbit.plot([0], [0], [0], '.k-', linewidth=0.5)
