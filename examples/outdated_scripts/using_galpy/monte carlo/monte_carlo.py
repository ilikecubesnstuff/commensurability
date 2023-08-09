import os
from tqdm import tqdm
from pathlib import Path
from itertools import count

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from utils import example, main

from multiprocessing import Pool


class OrbitalPhaseSlice:

    def __init__(self):
        pass


FORMAT = '.npz'
class OrbitalPhaseSpace:

    def __init__(self, name, potential, t, dt, ic_format=('R', 'vR', 'vT', 'z', 'vz', 'phi'), dims=('R', 'vT'), seed=None, data_folder=Path('.')):
        if len(dims) > 2:
            raise NotImplemented('Only 2 dimensions of the phase space can be analyzed in this class.')
        self.name = name
        self.potential = potential
        self.t = t
        self.dt = dt
        self.ic_format = ic_format
        self.x, self.y = dims
        self.rng = np.random.default_rng(seed=seed)

        filename = '_'.join((
            name.strip().replace(" ", "_"),
            '_'.join(dims),
            str(t),
            str(dt)
        )) + FORMAT
        self.file = data_folder / filename
    

    @property
    def generated(self):
        return self.file.is_file()


    def load_into_array(self, shape, extent):
        if not self.generated:
            values = np.zeros(shape)
            nearest = np.ones(shape) * np.inf
            return values, nearest
        xres, yres = shape
        xmin, xmax, ymin, ymax = extent
        name = f'{xmin}_{xmax}_{xres}__{ymin}_{ymax}_{yres}'

        npzfile = np.load(self.file)
        if name + '__values' not in npzfile:
            values = np.zeros(shape)
            nearest = np.ones(shape) * np.inf
            # data = npzfile['raw']
        else:
            values = npzfile[name + '__values']
            nearest = npzfile[name + '__nearest']
            # maxi ,= npzfile[name + '__size']
            # data = npzfile['raw'][maxi:]

        # dx = (xmax - xmin) / xres
        # dy = (ymax - ymin) / yres
        # xinds, yinds = np.meshgrid(np.arange(xres), np.arange(yres))
        # for x, y, value in tqdm(data, desc='loading data'):
        #     xi = (x - xmin) / dx
        #     yi = (y - ymin) / dy

        #     dists = abs(xinds - xi) + abs(yinds - yi)
        #     mask = (dists < nearest)
        #     if not np.sum(mask):
        #         continue

        #     values[mask] = value
        #     nearest[mask] = dists[mask]
        return values, nearest


    def measure(self, ic):
        o = orbit.Orbit(ic)
        t = np.arange(0, self.t, self.dt) * u.Gyr
        o.integrate(t, self.potential, method='dopr54_c')
        tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
        return tess.area


    def generate_data_points(self, xrange, yrange, N=None, liveplot=False):
        if self.generated:
            npzfile = np.load(self.file)
            print(npzfile)
            # existing_data = npzfile['raw']
        # else:
        #     existing_data = np.array([])
        data = []
        xres = yres = 2000  # arbitrary!
        shape = (xres, yres)
        xmin, xmax = xrange
        ymin, ymax = yrange
        dx = (xmax - xmin) / xres
        dy = (ymax - ymin) / yres
        xinds, yinds = np.meshgrid(np.arange(xres), np.arange(yres))
        extent = (*xrange, *yrange)
        values, nearest = self.load_into_array(shape, extent)

        if liveplot:
            plt.ion()
            fig, (ax_v, ax_n) = plt.subplots(1, 2, figsize=(12, 5))
            plt_values = ax_v.imshow(values, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=extent, aspect=dx/dy)
            fig.colorbar(plt_values, ax=ax_v)
            plt_nearest = ax_n.imshow(nearest, cmap='inferno', vmin=0, vmax=min(1000, np.max(nearest)), origin='lower', extent=extent, aspect=dx/dy)
            fig.colorbar(plt_nearest, ax=ax_n)

            def on_close(event):
                print('saving on close...')
                # arr = np.vstack((existing_data, data)) if existing_data.size > 0 else data
                name = f'{xmin}_{xmax}_{xres}__{ymin}_{ymax}_{yres}'
                dd = {
                    name + '__values': values,
                    name + '__nearest': nearest,
                    # name + '__size': [len(arr)]
                }
                np.savez(self.file, **dd)
            fig.canvas.mpl_connect('close_event', on_close)

        it = tqdm(range(N)) if N else tqdm(count())
        try:
            for _ in it:
                x = self.rng.uniform(*xrange)
                y = self.rng.uniform(*yrange)
                ic = [
                    x * u.kpc,
                    0 * u.km / u.s, 
                    y * u.km / u.s, 
                    0 * u.kpc, 
                    0 * u.km / u.s, 
                    0 * u.deg
                ]
                value = self.measure(ic)
                data.append((x, y, value))

                xi = (x - xmin) / dx
                yi = (y - ymin) / dy

                dists = abs(xinds - xi) + abs(yinds - yi)
                mask = (dists < nearest)
                if not np.sum(mask):
                    continue
                
                values[mask] = value
                nearest[mask] = dists[mask]

                if liveplot:
                    plt_values.set_data(values)
                    plt_nearest.set_data(nearest)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
        finally:
            print('saving...')
            # npzfile = np.load(self.file)
            # npzfile['raw'] = np.vstack((existing_data, data)) if existing_data.size > 0 else data
            name = f'{xmin}_{xmax}_{xres}__{ymin}_{ymax}_{yres}'
            dd = {
                name + '__values': values,
                name + '__nearest': nearest
            }
            np.savez(self.file, **dd)
            print('saved!')


@example(default=True)
def default(liveplot=False):
    pot = [
        potential.NFWPotential(
            conc = 10,
            mvir = 1,
        ),
        potential.MiyamotoNagaiPotential(
            amp = 5e10 * u.solMass,
            a = 3 * u.kiloparsec,
            b = 0.1 * u.kiloparsec,
        ),
        potential.SoftenedNeedleBarPotential(
            amp = 10e9 * u.solMass,
            a = 1.5 * u.kiloparsec,
            b = 0 * u.kiloparsec,
            c = 0.5 * u.kiloparsec,
            omegab = 30 * u.km / u.s / u.kpc
        ),
        potential.NonInertialFrameForce(
            Omega = 30 * u.km / u.s / u.kpc
        )
    ]
    oph = OrbitalPhaseSpace('rotbar', pot, 2, 0.005)

    xrange = [0, 10]; yrange = [0, 600]
    # xrange = [0, 3]; yrange = [200, 400]
    # xrange = [0, 2.5]; yrange = [400, 600]
    # xrange = [2, 6]; yrange = [0, 200]
    # xrange = [2, 4]; yrange = [100, 200]
    oph.generate_data_points(xrange=xrange, yrange=yrange, liveplot=liveplot)
    # oph.generate_data_points(xrange=xrange, yrange=yrange, liveplot=True, N=10)
    # oph.plot()


@example()
def live():
    default(liveplot=True)


if __name__ == '__main__':
    main()