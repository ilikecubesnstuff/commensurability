import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from galpy import potential, orbit

from commensurability.tessellation import Tessellation

from tqdm import tqdm
from timeit import timeit


omega = 30 * u.km/u.s/u.kpc
pot = [
    potential.NFWPotential(conc=10, mvir=1),
    potential.MiyamotoNagaiPotential(amp=5e10 * u.solMass, a=3 * u.kpc, b=0.1 * u.kpc),
    potential.SoftenedNeedleBarPotential(amp=1e9 * u.solMass, a=1.5 * u.kpc, b=0 * u.kpc, c=0.5 * u.kpc, omegab=omega),
    potential.NonInertialFrameForce(Omega=omega)
]
ts = np.linspace(0, 1, 400) * u.Gyr
def run_test(N=1000):
    ic = [
        np.random.random() * u.kpc, 
        np.random.random() * u.km/u.s, 
        np.random.random() * u.km/u.s, 
        np.random.random() * u.kpc, 
        np.random.random() * u.km/u.s, 
        np.random.random() * u.deg
    ]
    o = orbit.Orbit(ic)
    o.integrate(ts, pot, method="dopr54_c")

    tess = Tessellation.from_galpy_orbit(o)
    print(tess.volume)
    tess.plot_tessellation_trimming()



def orbit_test(N):
    setup = '''
ts = np.linspace(0, 4, N)
ic = [
    np.random.random() * u.kpc, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.kpc, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.deg
]
o = orbit.Orbit(ic)
    '''

    stmt = 'o.integrate(ts, pot, method="dopr54_c")'

    return timeit(stmt, setup, number=100, globals=globals() | locals())

def orbit_range(Ns):
    result = [orbit_test(N) for N in tqdm(Ns)]
    plt.plot(Ns, result)
    plt.show()


def tess_test(N):
    setup = '''
ts = np.linspace(0, 4, N)
ic = [
    np.random.random() * u.kpc, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.kpc, 
    np.random.random() * u.km/u.s, 
    np.random.random() * u.deg
]
o = orbit.Orbit(ic)
o.integrate(ts, pot, method="dopr54_c")
    '''

    stmt = 'tess = Tessellation.from_galpy_orbit(o)'

    return timeit(stmt, setup, number=10, globals=globals() | locals())

def tess_range(Ns):
    result = [tess_test(N) for N in tqdm(Ns)]
    plt.plot(Ns, result)
    plt.show()


def main():
    # orbit_range(np.arange(0, 300, 10) + 10)
    tess_range(np.arange(500)[::-1] + 10)

if __name__ == '__main__':
    main()
