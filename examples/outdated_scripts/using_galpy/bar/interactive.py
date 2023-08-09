from tqdm import tqdm
from itertools import count

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from multiprocessing import Pool

# bar mass, in solar masses
OMEGA_MIN = 0e9  # solMass
OMEGA_MAX = 1e9  # solMass
FRAMES = 11

# range of R (cylindrical coordinates), in kiloparsecs
R_MIN = 0  # kpc
R_MAX = 8  # kpc
# range of tangential velocity, in kilometers per second
VT_MIN = 0  # km/s
VT_MAX = 400  # km/s
# integration parameters, in gigayears
STEPSIZE = 0.001  # Gyr
STEPS = 1000

# name
NAME = 'MW_BAR_STILL'

FILENAME = f'{NAME}_over_OMEGA_{OMEGA_MIN}-{OMEGA_MAX}__R_{R_MIN}-{R_MAX}__VT_{VT_MIN}-{VT_MAX}__INT_{STEPSIZE}_{STEPS}.npy'


# ----------------------------------------------------
# helpful variables
X_RANGE = (R_MIN, R_MAX)
Y_RANGE = (VT_MIN, VT_MAX)
EXTENT = (R_MIN, R_MAX, VT_MIN, VT_MAX)
ASPECT = (R_MAX - R_MIN) / (VT_MAX - VT_MIN)

# data arrays
OMEGA_ARR = np.linspace(OMEGA_MIN, OMEGA_MAX, FRAMES)  * u.solMass
T_ARR = np.arange(0, STEPSIZE * STEPS, STEPSIZE)  * u.Gyr

# potential
omega_rot = 0 * u.km/u.s/u.kpc
halo = potential.NFWPotential(conc=10, mvir=1)
disc = potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc)
rotpot_factory = lambda omega: [
    halo,
    disc,
    potential.SoftenedNeedleBarPotential(amp=omega, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega_rot),
    potential.NonInertialFrameForce(Omega=omega_rot)
]
potentials = [rotpot_factory(omega) for omega in OMEGA_ARR]
def compute_orbit(ic, pot):
    o = orbit.Orbit(ic)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'), trim=None)
    return tess.points.T

def compute_tessellation(ic, pot):
    o = orbit.Orbit(ic)
    o.integrate(T_ARR, pot, method='dopr54_c')

    tess = Tessellation.from_galpy_orbit(o, dims=('x', 'y'))
    return tess


def main():
    cube = np.load(FILENAME)
    frame = 0
    
    fig, (ax_phase, ax_orbit) = plt.subplots(1, 2, figsize=(12, 5))

    # left: phase space
    omega = OMEGA_ARR[frame]
    ax_phase.set_title(f'{omega = }')
    im_phase = ax_phase.imshow(cube[frame].T, cmap='inferno', vmin=0, vmax=1, origin='lower', extent=EXTENT, aspect=ASPECT)
    dot_phase, = ax_phase.plot([R_MIN], [VT_MIN], 'go')

    # right: orbit in configuration space
    l_orbit, = ax_orbit.plot([0], [0], '.k-', linewidth=0.5)
    tri_l_orbit = None
    tri_m_orbit = None

    def on_click(event):
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
                0 * u.kpc, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            X, Y = compute_orbit(ic, potentials[frame])

            # draw orbit
            l_orbit.set_xdata(X)
            l_orbit.set_ydata(Y)
            Xrange = max(abs(X))
            Yrange = max(abs(Y))
            XYrange = max(Xrange, Yrange)
            ax_orbit.set_xlim([-XYrange, XYrange])
            ax_orbit.set_ylim([-XYrange, XYrange])
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
                0 * u.kpc, 
                0 * u.km / u.s, 
                0 * u.deg
            ]
            tess = compute_tessellation(ic, potentials[frame])
            X, Y = tess.points.T

            # draw orbit
            l_orbit.set_xdata(X)
            l_orbit.set_ydata(Y)
            Xrange = max(abs(X))
            Yrange = max(abs(Y))
            XYrange = max(Xrange, Yrange)
            ax_orbit.set_xlim([-XYrange, XYrange])
            ax_orbit.set_ylim([-XYrange, XYrange])
            ax_orbit.set_title(f'{R = }, {vT = }')

            tri_l_orbit, tri_m_orbit = ax_orbit.triplot(X, Y, tess.tri.simplices, mask=~tess.mask, color='green')
            ax_orbit.set_title(f'{tess.area = }')

            # update
            fig.canvas.draw()
            fig.canvas.flush_events()
    click_cid = fig.canvas.mpl_connect('button_press_event', on_click)
    
    def on_scroll(event):
        nonlocal frame, omega
        nonlocal tri_l_orbit, tri_m_orbit

        # update frame
        frame += int(event.step)
        frame = min(FRAMES - 1, max(0, frame))
        omega = OMEGA_ARR[frame]

        # redraw plots
        im_phase.set_data(cube[frame].T)
        ax_phase.set_title(f'{omega = }')
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