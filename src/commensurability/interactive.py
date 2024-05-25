"""
This module defines abstract base classes for interactive plots of phase space
slices alongside orbits in configuration space. The "dimensionality" associated
with the class corresponds with the dimensionality of the relevant orbits.

This module also defines user-facing interactive plot classes for 2D and 3D orbits.
"""

import gc
import warnings
from abc import abstractmethod
from typing import Any, Optional, Union

import matplotlib.pyplot as plt


class InteractivePlotBase:
    """
    Base class for interactive plotting.

    This class provides methods for handling interactive plots.
    """

    def __init__(self, analysis: Any, x_axis: str, y_axis: str, var_axis: Optional[str] = None):
        """
        Initialize InteractivePlotBase instance.

        Args:
            analysis: Analysis object containing the data to plot.
            x_axis (str): Name of the x-axis parameter.
            y_axis (str): Name of the y-axis parameter.
            var_axis (Optional[str]): Name of the variable axis (optional).
        """
        self.analysis = analysis
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.var_axis = var_axis

        self.shape = analysis.shape
        axes = self.analysis.axis_names.copy()
        self.indices: list[int | None] = [0 for ax in axes]
        self.indices[axes.index(self.x_axis)] = None
        self.indices[axes.index(self.y_axis)] = None

        XMIN = self.analysis.ic_values[self.x_axis][0]
        XMAX = self.analysis.ic_values[self.x_axis][-1]
        YMIN = self.analysis.ic_values[self.y_axis][0]
        YMAX = self.analysis.ic_values[self.y_axis][-1]
        XSTEP = self.analysis.ic_values[self.x_axis][1] - self.analysis.ic_values[self.x_axis][0]
        YSTEP = self.analysis.ic_values[self.y_axis][1] - self.analysis.ic_values[self.y_axis][0]
        self.extent = (XMIN - XSTEP / 2, XMAX + XSTEP / 2, YMIN - YSTEP / 2, YMAX + YSTEP / 2)
        self.aspect = (XMAX - XMIN) / (YMAX - YMIN)

        axes.remove(x_axis)
        axes.remove(y_axis)
        if self.var_axis is None:
            self.var_axis = axes[0] if axes else None

    @staticmethod
    def image_slice(data: Any, indices: list[Union[int, None]]) -> Any:
        """
        Return a 2D slice of the analysis data according to the given indices.

        Args:
            data: Analysis data.
            indices: Indices to slice the data with, marked with two `None`s.

        Returns:
            Sliced image data.
        """
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
        self.indices[i] = max(0, min(self.analysis.ic_values[self.var_axis].size - 1, new))

        info = [
            f"{ax}={self.analysis.ic_values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        image = self.image_slice(self.analysis.measures, self.indices).T
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
            # NOTE: Various objects seems to be in the garbage list when not existing
            # within the plot's object list. For now, I will pass in these cases.
            # I have no clue what these objects are. This may lead to memory problems
            # in extreme cases, but for now they appear harmless.
            try:
                thing.remove()
            except ValueError:
                pass
            del thing

        # to counteract the above memory concerns, run gc.collect here
        gc.collect()

        if event.button == 1:
            self.on_left_click(event)
        if event.button == 3:
            self.on_right_click(event)

    def _mpl_scroll_event(self, event):
        if event.inaxes is not self.ax_phase:
            return

        for thing in self.garbage:
            # NOTE: Various objects seems to be in the garbage list when not existing
            # within the plot's object list. For now, I will pass in these cases.
            # I have no clue what these objects are. This may lead to memory problems
            # in extreme cases, but for now they appear harmless.
            try:
                thing.remove()
            except ValueError:
                pass
            del thing

        # to counteract the above memory concerns, run gc.collect here
        gc.collect()

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

    def show(self, **imshow_kwargs: dict[str, Any]):
        """
        Show the interactive plot.

        Args:
            **imshow_kwargs: Additional keyword arguments for plt.imshow.
        """
        self.plot_axes(**imshow_kwargs)
        self.garbage: set = set()

        # connect methods to figure
        self._add_connections()
        plt.show()

    @abstractmethod
    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        """
        Plot the axes.

        Args:
            **imshow_kwargs: Additional keyword arguments for imshow.
        """
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122)


class InteractivePlot2D(InteractivePlotBase):
    """
    Interactive plotting class for 2D orbits.

    This class extends InteractivePlotBase and provides methods for interactive 2D plots.
    """

    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
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
        value = self.analysis.evaluate(orbit).measure

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

    def on_right_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
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
        value = self.analysis.evaluate(orbit).measure

        # for 2D plot
        X, Y, Z = orbit.xyz
        self.l_orbit.set_data(X, Y)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        XYrange = max(Xrange, Yrange)
        self.ax_orbit.set_xlim([-XYrange, XYrange])
        self.ax_orbit.set_ylim([-XYrange, XYrange])

        # plot evaluation of the orbit
        extras = self.analysis.evaluate(orbit).plot(self.ax_orbit)
        self.garbage.update(extras)

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        """
        Plot the axes.

        Args:
            **imshow_kwargs: Additional keyword arguments for imshow.
        """
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
        image = self.image_slice(self.analysis.measures, self.indices).T
        self.im_phase = self.ax_phase.imshow(image, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([self.extent[0]], self.extent[2])

        self.ax_phase.set_xlabel(self.x_axis)
        self.ax_phase.set_ylabel(self.y_axis)
        info = [
            f"{ax}={self.analysis.ic_values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], ".k-", linewidth=0.5)


class InteractivePlot3D(InteractivePlotBase):
    """
    Interactive plotting class for 3D orbits.

    This class extends InteractivePlotBase and provides methods for interactive 3D plots.
    """

    def on_left_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
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
        value = self.analysis.evaluate(orbit).measure

        # for 3D plot
        X, Y, Z = orbit.xyz
        self.l_orbit.set_data_3d(X, Y, Z)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        Zrange = max(abs(Z))
        XYZrange = max(Xrange, Yrange, Zrange).value
        self.ax_orbit.set_xlim([-XYZrange, XYZrange])
        self.ax_orbit.set_ylim([-XYZrange, XYZrange])
        self.ax_orbit.set_zlim([-XYZrange, XYZrange])

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_right_click(self, event):
        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
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
        value = self.analysis.evaluate(orbit).measure

        # for 3D plot
        X, Y, Z = orbit.xyz
        self.l_orbit.set_data_3d(X, Y, Z)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        Zrange = max(abs(Z))
        XYZrange = max(Xrange, Yrange, Zrange).value
        self.ax_orbit.set_xlim([-XYZrange, XYZrange])
        self.ax_orbit.set_ylim([-XYZrange, XYZrange])
        self.ax_orbit.set_zlim([-XYZrange, XYZrange])

        # plot evaluation of the orbit
        extras = self.analysis.evaluate(orbit).plot(self.ax_orbit)
        self.garbage.update(extras)

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        """
        Plot the axes.

        Args:
            **imshow_kwargs: Additional keyword arguments for imshow.
        """
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
        image = self.image_slice(self.analysis.measures, self.indices).T
        self.im_phase = self.ax_phase.imshow(image, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([self.extent[0]], self.extent[2])

        self.ax_phase.set_xlabel(self.x_axis)
        self.ax_phase.set_ylabel(self.y_axis)
        info = [
            f"{ax}={self.analysis.ic_values[ax][i]}"
            for ax, i in zip(self.analysis.axis_names, self.indices)
            if i is not None
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], [0], ".k-", linewidth=0.5)
