from abc import abstractmethod

import matplotlib.pyplot as plt


class InteractivePlotBase:
    def __init__(self, analysis, x_axis, y_axis, var_axis=None):
        self.analysis = analysis
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.var_axis = var_axis

        self.shape = analysis.shape
        axes = self.analysis.axis_names.copy()
        self.indices = [0 for ax in axes]
        self.indices[axes.index(self.x_axis)] = None
        self.indices[axes.index(self.y_axis)] = None

        XMIN = self.analysis.values[self.x_axis][0]
        XMAX = self.analysis.values[self.x_axis][-1]
        YMIN = self.analysis.values[self.y_axis][0]
        YMAX = self.analysis.values[self.y_axis][-1]
        self.extent = (XMIN, XMAX, YMIN, YMAX)
        self.aspect = (XMAX - XMIN) / (YMAX - YMIN)

        axes.remove(x_axis)
        axes.remove(y_axis)
        if self.var_axis is None:
            self.var_axis = axes[0] if axes else None

    @staticmethod
    def image_slice(data, indices):
        i = indices.index(None)
        j = indices.index(None, i + 1)
        image = data[*indices[:i], :, *indices[i + 1 : j], :, *indices[j + 1 :]]
        return image

    def on_right_click(self, event):
        print("Right-click not implemented yet!")

    def on_left_click(self, event):
        print("Left-click not implemented yet!")

    def on_scroll(self, event):
        if not self.var_axis:
            return

        i = self.analysis.axis_names.index(self.var_axis)
        new = self.indices[i] + int(event.step)
        # clip the value inside the valid index range
        self.indices[i] = max(0, min(self.analysis.values[self.var_axis].size - 1, new))

        info = [
            f"{ax}={self.analysis.values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        image = self.image_slice(self.analysis.image, self.indices).T
        self.im_phase.set_data(image)

        # reset the rest
        self.dot_phase.set_xdata([self.extent[0]])
        self.dot_phase.set_ydata([self.extent[2]])
        self.l_orbit.set_xdata([0])
        self.l_orbit.set_ydata([0])

        # udpate figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_keypress(self, event):
        print("Key press not implemented yet!")
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
            self.fig.canvas.mpl_connect("button_press_event", self._mpl_button_press_event)
        )
        self.connections.append(self.fig.canvas.mpl_connect("scroll_event", self._mpl_scroll_event))
        self.connections.append(
            self.fig.canvas.mpl_connect("key_press_event", self._mpl_key_press_event)
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
        self.ax_orbit = self.fig.add_subplot(122)


class InteractivePlot2D(InteractivePlotBase):
    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.values[ax][i]
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        }
        values[self.x_axis] = event.xdata
        values[self.y_axis] = event.ydata
        coord = self.analysis.ic_function(**values)

        orbit = self.analysis.backend.compute_orbit(
            coord,
            pot=self.analysis.potential,
            dt=self.analysis.dt,
            steps=self.analysis.steps,
            pattern_speed=self.analysis.pattern_speed,
        )
        value = self.analysis.__eval__(orbit)

        # for 2D plot
        X, Y, Z = orbit.xyz
        self.l_orbit.set_data(X, Y)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        XYrange = max(Xrange, Yrange)
        self.ax_orbit.set_xlim([-XYrange, XYrange])
        self.ax_orbit.set_ylim([-XYrange, XYrange])

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def plot_axes(self, **imshow_kwargs):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122)

        # left plot: phase space
        kwargs = dict(
            origin="lower",
            cmap="inferno",
            vmin=0,
            vmax=1,
            extent=self.extent,
            aspect=self.aspect,
        )
        kwargs.update(**imshow_kwargs)
        image = self.image_slice(self.analysis.image, self.indices).T
        self.im_phase = self.ax_phase.imshow(image, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([self.extent[0]], self.extent[2])

        self.ax_phase.set_xlabel(self.x_axis)
        self.ax_phase.set_ylabel(self.y_axis)
        info = [
            f"{ax}={self.analysis.values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], ".k-", linewidth=0.5)


class InteractivePlot3D(InteractivePlotBase):
    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.values[ax][i]
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        }
        values[self.x_axis] = event.xdata
        values[self.y_axis] = event.ydata
        coord = self.analysis.ic_function(**values)

        orbit = self.analysis.backend.compute_orbit(
            coord,
            pot=self.analysis.potential,
            dt=self.analysis.dt,
            steps=self.analysis.steps,
            pattern_speed=self.analysis.pattern_speed,
        )
        value = self.analysis.__eval__(orbit)

        # for 3D plot
        X, Y, Z = orbit.xyz
        self.l_orbit.set_data_3d(X, Y, Z)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        Zrange = max(abs(Z))
        XYZrange = max(Xrange, Yrange, Zrange)
        self.ax_orbit.set_xlim([-XYZrange, XYZrange])
        self.ax_orbit.set_ylim([-XYZrange, XYZrange])
        self.ax_orbit.set_zlim([-XYZrange, XYZrange])

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_right_click(self, event):
        print("Right-click not implemented yet!")
        # TODO: plot orbit with tessellation on right plot

    def plot_axes(self, **imshow_kwargs):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122, projection="3d")

        # left plot: phase space
        kwargs = dict(
            origin="lower",
            cmap="inferno",
            vmin=0,
            vmax=1,
            extent=self.extent,
            aspect=self.aspect,
        )
        kwargs.update(**imshow_kwargs)
        image = self.image_slice(self.analysis.image, self.indices).T
        self.im_phase = self.ax_phase.imshow(image, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([self.extent[0]], self.extent[2])

        self.ax_phase.set_xlabel(self.x_axis)
        self.ax_phase.set_ylabel(self.y_axis)
        info = [
            f"{ax}={self.analysis.values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], [0], ".k-", linewidth=0.5)
