from tqdm import tqdm
from itertools import count

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool

# omega parameter values, in kilometers per second per kiloparsec
Z_MIN = 0  # km/s/kpc
Z_MAX = 6  # km/s/kpc
FRAMES = 50

# range of R (cylindrical coordinates), in kiloparsecs
R_MIN = 0  # kpc
R_MAX = 10  # kpc
# range of tangential velocity, in kilometers per second
VT_MIN = 0  # km/s
VT_MAX = 600  # km/s
# integration parameters, in gigayears
STEPSIZE = 0.005  # Gyr
STEPS = 400

# name
NAME = 'MW_BARLESS'
# save location
FILENAME = f'rotbar_R_vT.npz'


# ----------------------------------------------------
# helpful variables
X_RANGE = (R_MIN, R_MAX)
Y_RANGE = (VT_MIN, VT_MAX)
EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)

# data arrays
Z_ARR = np.linspace(Z_MIN, Z_MAX, FRAMES)  * u.kpc
T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr

# potentials
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
rotpot_factory = lambda omega: [
    halo,
    disc,
    potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
    potential.NonInertialFrameForce(Omega = omega)
]

omega = 30  * u.km/u.s/u.kpc
POTENTIAL = rotpot_factory(omega=omega)
def compute_orbit(ic, pot):
    o = orbit.Orbit(ic)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, trim=None)
    return tess.points.T

def compute_tessellation(ic, pot):
    o = orbit.Orbit(ic)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o)
    return tess


def main():
    npzfile = np.load(FILENAME)
    cube = npzfile['values']
    frame = 0

    fig = plt.figure(figsize=(12, 5))
    ax_phase = fig.add_subplot(121)
    ax_orbit = fig.add_subplot(122, projection='3d')

    # fig, (ax_phase, ax_orbit) = plt.subplots(1, 2, figsize=(12, 5),)

    # left: phase space
    z = Z_ARR[frame]
    ax_phase.set_title(f'{z = }')
    im_phase = ax_phase.imshow(cube[:,:,frame], cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
    dot_phase, = ax_phase.plot([R_MIN], [VT_MIN], 'go')

    # right: orbit in configuration space
    l_orbit, = ax_orbit.plot([0], [0], [0], '.k-', linewidth=0.5)
    tri_l_orbit = None
    tri_m_orbit = None

    def on_click(event):
        if event.inaxes is not ax_phase:
            return

        nonlocal tri_l_orbit, tri_m_orbit
        if tri_l_orbit:
            tri_l_orbit.remove()
            tri_l_orbit = None
        if tri_m_orbit:
            tri_m_orbit.remove()
            tri_m_orbit = None

        if event.button == 1:
            print(event.xdata, event.ydata)
            # move dot in phase space
            dot_phase.set_xdata([event.xdata])
            dot_phase.set_ydata([event.ydata])

            # compute orbit
            R = event.xdata * u.kpc
            vT = event.ydata * u.km / u.s
            ic = [
                R,
                0 * u.km / u.s, 
                vT, 
                z, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            X, Y, Z = compute_orbit(ic, POTENTIAL)

            # draw orbit
            l_orbit.set_data_3d(X, Y, Z)
            Xrange = max(abs(X))
            Yrange = max(abs(Y))
            Zrange = max(abs(Z))
            XYZrange = max(Xrange, Yrange, Zrange)
            ax_orbit.set_xlim([-XYZrange, XYZrange])
            ax_orbit.set_ylim([-XYZrange, XYZrange])
            ax_orbit.set_zlim([-XYZrange, XYZrange])
            # Xrange = max(abs(X))
            # Yrange = max(abs(Y))
            # Zrange = max(abs(Z))
            # XYrange = max(Xrange, Yrange)
            # ax_orbit.set_xlim([-XYrange, XYrange])
            # ax_orbit.set_ylim([-XYrange, XYrange])
            # ax_orbit.set_zlim([-Zrange, Zrange])
            ax_orbit.set_title(f'{R = }, {vT = }')

            # update
            fig.canvas.draw()
            fig.canvas.flush_events()

        if event.button == 3:
            print(event.xdata, event.ydata)
            # move dot in phase space
            dot_phase.set_xdata([event.xdata])
            dot_phase.set_ydata([event.ydata])

            # compute orbit
            R = event.xdata * u.kpc
            vT = event.ydata * u.km / u.s
            ic = [
                R,
                0 * u.km / u.s, 
                vT, 
                z, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            tess = compute_tessellation(ic, POTENTIAL)
            X, Y, Z = tess.points.T

            # draw orbit
            l_orbit.set_data_3d(X, Y, Z)
            Xrange = max(abs(X))
            Yrange = max(abs(Y))
            Zrange = max(abs(Z))
            XYZrange = max(Xrange, Yrange, Zrange)
            ax_orbit.set_xlim([-XYZrange, XYZrange])
            ax_orbit.set_ylim([-XYZrange, XYZrange])
            ax_orbit.set_zlim([-XYZrange, XYZrange])
            # Xrange = max(abs(X))
            # Yrange = max(abs(Y))
            # Zrange = max(abs(Z))
            # XYrange = max(Xrange, Yrange)
            # ax_orbit.set_xlim([-XYrange, XYrange])
            # ax_orbit.set_ylim([-XYrange, XYrange])
            # ax_orbit.set_zlim([-Zrange, Zrange])

            # triangulation lines
            g_conns = set()
            r_conns = set()
            for simplex, included in zip(tess.tri.simplices, tess.mask):
                i1, i2, i3, i4 = sorted(simplex)
                conns = g_conns if included else r_conns
                conns.add((i1, i2))
                conns.add((i1, i3))
                conns.add((i1, i4))
                conns.add((i2, i3))
                conns.add((i2, i4))
                conns.add((i3, i4))

            # plot triangulation
            lines = [(tess.points[i1], tess.points[i2]) for i1, i2 in g_conns]
            tri_l_orbit = a3.art3d.Poly3DCollection(lines)
            tri_l_orbit.set_edgecolor('g')
            tri_l_orbit.set_linewidths(0.5)
            ax_orbit.add_collection3d(tri_l_orbit)
            # tri_m_orbit = ax_orbit.scatter(X, Y, Z, marker='.', color='black')
            ax_orbit.set_title(f'{tess.volume = }')

            # update
            fig.canvas.draw()
            fig.canvas.flush_events()
    click_cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    def on_scroll(event):
        nonlocal frame, z
        nonlocal tri_l_orbit, tri_m_orbit

        # update frame
        frame += int(event.step)
        frame = min(FRAMES - 1, max(0, frame))
        z = Z_ARR[frame]

        # redraw plots
        im_phase.set_data(cube[:,:,frame])
        ax_phase.set_title(f'{z = }')
        dot_phase.set_xdata([R_MIN])
        dot_phase.set_ydata([VT_MIN])

        l_orbit.set_xdata([0])
        l_orbit.set_ydata([0])
        if tri_l_orbit:
            tri_l_orbit.remove()
            tri_l_orbit = None
        if tri_m_orbit:
            tri_m_orbit.remove()
            tri_m_orbit = None

        # update
        fig.canvas.draw()
        fig.canvas.flush_events()
    scroll_cid = fig.canvas.mpl_connect('scroll_event', on_scroll)

    plt.show()

if __name__ == '__main__':
    main()