from typing import Any, Optional, Callable
import gc

import numpy as np
import matplotlib.pyplot as plt

import pidgey

FULL_AXIS = slice(None)


class Viewer:
    def __init__(
            self,
            nd_image: np.ndarray,
            axlims: dict[str: list[float, float]],
            x_axis: Optional[str] = None,
            y_axis: Optional[str] = None,
            s_axis: Optional[str] = None,
    ):
        self.im: np.ndarray = nd_image
        self.shape = nd_image.shape
        if len(self.shape) < 2:
            return ValueError('Cannot display plot for image with less than 2 dimensions.')

        self.axnames = list(axlims.keys())
        self.axvalues = [
            np.linspace(vmin, vmax, n) for n, (vmin, vmax) in zip(self.shape, axlims.values())
        ]
        self.axsteps = [
            (vmax - vmin) / (n - 1) for n, (vmin, vmax) in zip(self.shape, axlims.values())
        ]

        if all(ax == None for ax in [x_axis, y_axis, s_axis]):
            x_axis = 0
            y_axis = 1
            s_axis = 2 if len(self.shape) > 2 else None
        elif any(ax == None for ax in [x_axis, y_axis, s_axis]):
            raise ValueError('All of x_axis, y_axis, and s_axis must be given.')

        self.ihax = x_axis
        self.ivax = y_axis
        self.isax = s_axis

        self.cursor = [0] * len(self.shape)
        self.cursor[self.ihax] = FULL_AXIS
        self.cursor[self.ivax] = FULL_AXIS

        self.scroll_plane = self.slice_for_scroll()


    # === SLICING METHODS ===

    def slice_for_scroll(self):
        cursor = self.cursor.copy()
        cursor[self.ihax] = FULL_AXIS
        cursor[self.ivax] = FULL_AXIS
        if self.isax: cursor[self.isax] = FULL_AXIS
        if sum(i == FULL_AXIS for i in cursor) > 3:
            raise ValueError('pivot not set!')

        axes = np.argsort([self.ihax, self.ivax, self.isax] if self.isax else [self.ihax, self.ivax])
        axes = np.argsort(axes)  # require inverse permutation
        return self.im[tuple(cursor)].transpose(axes)

    def slice_for_plot(self):
        if not self.isax:
            return self.scroll_plane
        return self.scroll_plane[..., self.cursor[self.isax]]


    # === EVENT METHODS ===

    def update_plot(self):
        plot_plane = self.slice_for_plot()
        self.viewer_image.set_data(plot_plane.T)

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax.set_title(", ".join(info))

        self.ax.set_xlabel(self.axnames[self.ihax])
        self.ax.set_ylabel(self.axnames[self.ivax])

        # update figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def on_left_click(self, event):
        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return

        xlims = self.axvalues[self.ihax]
        ylims = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]

        xi = np.searchsorted(xlims, x - xstep/2)
        yi = np.searchsorted(ylims, y - ystep/2)

        self.cursor[self.ihax] = xi
        self.cursor[self.ivax] = yi

    def on_scroll(self, event):
        if not self.isax:
            return

        new_index = self.cursor[self.isax] + int(event.step)
        self.cursor[self.isax] = max(0, min(self.shape[self.isax] - 1, new_index))

        self.update_plot()

    def on_keypress(self, event):
        log = []
        log.append(f'keypress {event.key}')

        if event.key.isdigit() and self.isax is not None:
            axis_index = int(event.key) - 1
            if axis_index > len(self.shape):
                return

            if self.ihax == axis_index:
                return
            if self.ivax == axis_index:
                return

            self.isax = axis_index
            self.scroll_plane = self.slice_for_scroll()
            log.append(f'scroll axis set to {self.axnames[self.isax]}')

        if event.key.count('+') == 1:
            key1, key2 = event.key.split('+')
            if not key2.isdigit():
                return
            if key1 not in ['ctrl', 'alt']:
                return
            if any(i == FULL_AXIS for i in self.cursor):
                raise ValueError('pivot not set, click on the plotting region to set a pivot')

            axis_index = int(key2) - 1
            if key1 == 'ctrl':
                if self.isax == axis_index:
                    self.isax = self.ihax  # swap axes
                    log.append(f'scroll axis set to {self.axnames[self.isax]}')
                if self.ivax == axis_index:
                    self.ivax = self.ihax  # swap axes
                    log.append(f'y axis set to {self.axnames[self.ivax]}')
                self.ihax = axis_index
                self.scroll_plane = self.slice_for_scroll()
                log.append(f'x axis set to {self.axnames[self.ihax]}')

            if key1 == 'alt':
                if self.isax == axis_index:
                    self.isax = self.ivax  # swap axes
                    log.append(f'scroll axis set to {self.axnames[self.isax]}')
                if self.ihax == axis_index:
                    self.ihax = self.ivax  # swap axes
                    log.append(f'x axis set to {self.axnames[self.ihax]}')
                self.ivax = axis_index
                self.scroll_plane = self.slice_for_scroll()
                log.append(f'y axis set to {self.axnames[self.ivax]}')
        print(', '.join(log))

        self.update_plot()


    # === MPL CONFIGURATION METHODS ===

    def _mpl_button_press_event(self, event):
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


    # === INITIAL PLOTTING METHOD ===

    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        """
        Plot the axes.

        Args:
            **imshow_kwargs: Additional keyword arguments for imshow.
        """
        self.fig = plt.figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax.set_title(", ".join(info))

        xmin, *_, xmax = self.axvalues[self.ihax]
        ymin, *_, ymax = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]

        kwargs = dict(
            origin="lower",
            cmap="inferno",
            vmin=0,
            vmax=1,
            extent=(xmin - xstep/2, xmax + xstep/2, ymin - ystep/2, ymax + ystep/2),
            aspect=(xmax - xmin) / (ymax - ymin),
        )
        kwargs.update(imshow_kwargs)
        plot_plane = self.slice_for_plot()
        self.ax.set_xlabel(self.axnames[self.ihax])
        self.ax.set_ylabel(self.axnames[self.ivax])
        self.viewer_image = self.ax.imshow(plot_plane.T, **kwargs)


class AnalysisViewer2D(Viewer):
    def __init__(
            self,
            analysis,
            x_axis: Optional[str] = None,
            y_axis: Optional[str] = None,
            s_axis: Optional[str] = None,
    ):
        self.analysis = analysis
        axlims = {name: [values[0], values[-1]] for name, values in analysis.ic_values.items()}
        super().__init__(
            nd_image=analysis.measures,
            axlims=axlims,
            x_axis=x_axis,
            y_axis=y_axis,
            s_axis=s_axis,
        )

    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122)

        # left plot: phase space
        xmin, *_, xmax = self.axvalues[self.ihax]
        ymin, *_, ymax = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]
        kwargs = dict(
            origin="lower",
            cmap="inferno",
            vmin=0,
            vmax=1,
            extent=(xmin - xstep/2, xmax + xstep/2, ymin - ystep/2, ymax + ystep/2),
            aspect=(xmax - xmin + xstep) / (ymax - ymin + ystep),
        )
        kwargs.update(**imshow_kwargs)
        plot_plane = self.slice_for_plot()
        self.ax_phase.set_xlabel(self.axnames[self.ihax])
        self.ax_phase.set_ylabel(self.axnames[self.ivax])
        self.im_phase = self.ax_phase.imshow(plot_plane.T, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([xmin - xstep/2], ymin - ystep/2, color='green')

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], ".k-", linewidth=0.5)

    def update_plot(self):
        plot_plane = self.slice_for_plot()
        self.im_phase.set_data(plot_plane.T)

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax_phase.set_title(", ".join(info))

        self.ax_phase.set_xlabel(self.axnames[self.ihax])
        self.ax_phase.set_ylabel(self.axnames[self.ivax])

        # update axes
        xmin, *_, xmax = self.axvalues[self.ihax]
        ymin, *_, ymax = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]
        self.im_phase.set_extent((xmin - xstep/2, xmax + xstep/2, ymin - ystep/2, ymax + ystep/2))
        self.ax_phase.set_aspect((xmax - xmin + xstep) / (ymax - ymin + ystep))

        # update figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_left_click(self, event):
        if event.inaxes is not self.ax_phase:
            return

        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        self.set_pivot(x, y)

        self.dot_phase.set_xdata([x])
        self.dot_phase.set_ydata([y])

        values = {
            ax: self.analysis.ic_values[ax][i]
            for ax, i in zip(self.axnames, self.cursor)
            if i is not None
        }
        values[self.axnames[self.ihax]] = event.xdata
        values[self.axnames[self.ivax]] = event.ydata
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
        self.l_orbit.set_data(X, Y)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        XYrange = max(Xrange, Yrange).value
        self.ax_orbit.set_xlim([-XYrange, XYrange])
        self.ax_orbit.set_ylim([-XYrange, XYrange])

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_right_click(self, event):
        if event.inaxes is not self.ax_phase:
            return

        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        self.set_pivot(x, y)

        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
            for ax, i in zip(self.axnames, self.cursor)
            if i is not None
        }
        values[self.axnames[self.ihax]] = event.xdata
        values[self.axnames[self.ivax]] = event.ydata
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
        self.l_orbit.set_data(X, Y)
        Xrange = max(abs(X))
        Yrange = max(abs(Y))
        XYrange = max(Xrange, Yrange).value
        self.ax_orbit.set_xlim([-XYrange, XYrange])
        self.ax_orbit.set_ylim([-XYrange, XYrange])

        # plot evaluation of the orbit
        extras = self.analysis.evaluate(orbit).plot(self.ax_orbit)
        self.garbage.update(extras)

        self.ax_orbit.set_title(f"{value = }")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class AnalysisViewer3D(Viewer):
    def __init__(
            self,
            analysis,
            x_axis: Optional[str] = None,
            y_axis: Optional[str] = None,
            s_axis: Optional[str] = None,
    ):
        self.analysis = analysis
        axlims = {name: [values[0], values[-1]] for name, values in analysis.ic_values.items()}
        super().__init__(
            nd_image=analysis.measures,
            axlims=axlims,
            x_axis=x_axis,
            y_axis=y_axis,
            s_axis=s_axis,
        )
    
    def set_pivot(self, x, y):
        xlims = self.axvalues[self.ihax]
        ylims = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]

        xi = np.searchsorted(xlims, x - xstep/2)
        yi = np.searchsorted(ylims, y - ystep/2)

        self.cursor[self.ihax] = xi
        self.cursor[self.ivax] = yi

    def plot_axes(self, **imshow_kwargs: dict[str, Any]):
        self.fig = plt.figure(figsize=(12, 5))
        self.ax_phase = self.fig.add_subplot(121)
        self.ax_orbit = self.fig.add_subplot(122, projection="3d")

        # left plot: phase space
        xmin, *_, xmax = self.axvalues[self.ihax]
        ymin, *_, ymax = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]
        kwargs = dict(
            origin="lower",
            cmap="inferno",
            vmin=0,
            vmax=1,
            extent=(xmin - xstep/2, xmax + xstep/2, ymin - ystep/2, ymax + ystep/2),
            aspect=(xmax - xmin + xstep) / (ymax - ymin + ystep),
        )
        kwargs.update(**imshow_kwargs)
        plot_plane = self.slice_for_plot()
        self.ax_phase.set_xlabel(self.axnames[self.ihax])
        self.ax_phase.set_ylabel(self.axnames[self.ivax])
        self.im_phase = self.ax_phase.imshow(plot_plane.T, **kwargs)
        (self.dot_phase,) = self.ax_phase.plot([xmin - xstep/2], ymin - ystep/2, color='green')

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax_phase.set_title(", ".join(info))

        # right plot: orbit in configuration space
        (self.l_orbit,) = self.ax_orbit.plot([0], [0], [0], ".k-", linewidth=0.5)

    def update_plot(self):
        plot_plane = self.slice_for_plot()
        self.im_phase.set_data(plot_plane.T)

        info = [
            f"{ax}={values[vi]}"
            for i, (ax, values, vi) in enumerate(zip(self.axnames, self.axvalues, self.cursor))
            if i not in [self.ihax, self.ivax]
        ]
        self.ax_phase.set_title(", ".join(info))

        self.ax_phase.set_xlabel(self.axnames[self.ihax])
        self.ax_phase.set_ylabel(self.axnames[self.ivax])

        # update axes
        xmin, *_, xmax = self.axvalues[self.ihax]
        ymin, *_, ymax = self.axvalues[self.ivax]
        xstep = self.axsteps[self.ihax]
        ystep = self.axsteps[self.ivax]
        self.im_phase.set_extent((xmin - xstep/2, xmax + xstep/2, ymin - ystep/2, ymax + ystep/2))
        self.ax_phase.set_aspect((xmax - xmin + xstep) / (ymax - ymin + ystep))

        # update figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def on_left_click(self, event):
        if event.inaxes is not self.ax_phase:
            return

        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        self.set_pivot(x, y)

        self.dot_phase.set_xdata([x])
        self.dot_phase.set_ydata([y])

        values = {
            ax: self.analysis.ic_values[ax][i]
            for ax, i in zip(self.axnames, self.cursor)
            if i is not None
        }
        values[self.axnames[self.ihax]] = event.xdata
        values[self.axnames[self.ivax]] = event.ydata
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
        if event.inaxes is not self.ax_phase:
            return

        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        self.set_pivot(x, y)

        self.dot_phase.set_xdata([event.xdata])
        self.dot_phase.set_ydata([event.ydata])

        values = {
            ax: self.analysis.ic_values[ax][i]
            for ax, i in zip(self.axnames, self.cursor)
            if i is not None
        }
        values[self.axnames[self.ihax]] = event.xdata
        values[self.axnames[self.ivax]] = event.ydata
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
