# Milky Way Orbit

```
from tessellation import Tessellation
```

Define a Milky Way potential with your package of choice.

=== "Agama"

    ``` py
    import agama
    from example_mw_bar_potential_new import makePotentialModel

    agama.setUnits(length=1, mass=1, velocity=1)  # 1 kpc, 1 Msun, 1 km/s
    potential = makePotentialModel()
    ```

    !!! note "Potential Definition"
        This example imports the Milky Way potential definition from [here](https://github.com/GalacticDynamics-Oxford/Agama/blob/master/py/example_mw_bar_potential_new.py).

=== "Gala"

    ``` py
    import gala.potential as gp

    potential = gp.MilkyWayPotential()
    ```

=== "Galpy"

    ``` py
    from galpy.potential import MWPotential2014

    potential = MWPotential2014
    ```

Perform an orbit integration routine.

=== "Agama"

    ``` py
    # x = 4 kpc, z = 1 kpc, vy = 250 km/s
    ic = [4, 0, 1, 0, 250, 0]
    ts, orbit = agama.orbit(potential=potential, ic=ic, time=1, trajsize=200)
    ```

=== "Gala"

    ``` py
    import astropy.units as u
    import gala.dynamics as gd

    # x = 4 kpc, z = 1 kpc, vy = 250 km/s
    ic = gd.PhaseSpacePosition(pos=[4, 0, 1] * u.kpc, vel=[0, 250, 0] * u.km/u.s)
    orbit = gp.Hamiltonian(potential).integrate_orbit(ic, dt=0.005 * u.Gyr, n_steps=200)
    ```

=== "Galpy"

    ``` py
    import numpy as np
    import astropy.units as u
    from galpy.orbit import Orbit

    # R = 4 kpc, z = 1 kpc, vT = 250 km/s
    orbit = Orbit([4 * u.kpc, 0 * u.km/u.s, 250 * u.km/u.s, 1 * u.kpc, 0 * u.km/u.s, 0 * u.deg])
    ts = np.linspace(0, 1, 200) * u.Gyr
    orbit.integrate(ts, potential)
    ```


`Tessellation` accepts the orbit object from the packages used in this example, but you have to specify the axes to extract (e.g. the "x", "y", and "z" axes).
(Agama works a little differently, so a point array is extracted directly.)

=== "Agama"

    ``` py
    # agama.orbit returns numpy arrays
    # extract point set in configuration space here
    points = orbit[:,:3]
    # tessellation accepts a point set in the form of a numpy array
    tess = Tessellation(points)
    ```

=== "Gala"

    ``` py
    tess = Tessellation(orbit, ('x', 'y', 'z'))
    ```

=== "Galpy"

    ``` py
    tess = Tessellation(orbit, ('x', 'y', 'z'))
    ```

The tessellation can then be plotted.

``` py
tess.plot(plot_removed=True)
```

=== "Agama"

    ![Agama orbit](mw_agama.png)

=== "Gala"

    ![Gala orbit](mw_gala.png)

=== "Galpy"

    ![Galpy orbit](mw_galpy.png)
