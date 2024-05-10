# Start Using `orbit-tessellation`

Follow the [installation](../installation.md) guide to install the package on your computer.

Although the [PyPI package](https://pypi.org/project/orbit-tessellation/) name is `orbit-tessellation`, the package is imported with the name `tessellation`. To get started, import `tessellation.Tessellation` and call it by passing in your point array.

```py
from tessellation import Tessellation
tess = Tessellation(points)
```

This should create a `Tessellation` object specific to the dimensionality of your points. (For dimensions larger than 3, a generic N-dimensional class is used.)

For a full walkthrough, see the [user guide](../user/index.md).

## Quick Examples

=== "2D Example"

    ``` py
    import numpy as np

    from tessellation import Tessellation

    # sample points around a circle with noise
    rng = np.random.default_rng(0)
    theta = rng.uniform(-np.pi, np.pi, 100)
    points = np.transpose([np.cos(theta), np.sin(theta)])
    points += rng.normal(0, 0.05, points.shape)

    # apply tessellation algorithm
    tess = Tessellation(points)

    print(tess)
    # Tessellation2D[measure=0.26383077462604737]
    print(tess.measure)
    # 0.26383077462604737
    print(tess.points)
    # [[ 0.58495528  0.68812897]
    #  [ 0.14913771 -0.94279612]
    #  ...
    #  [-0.81820176  0.66585581]
    #  [-0.45380873  0.91344067]]
    print(tess.tri.simplices)
    # [[73 60 70]
    #  [58 51  1]
    #  ...
    #  [38 78 73]
    #  [78 38 87]]
    print(tess.mask)
    # [False  True False False False False  True  True  True  True  True  True
    #   True  True  True  True  True False False  True  True  True  True  True
    #  ...
    #   True  True  True  True  True  True  True  True  True  True  True  True
    #   True  True  True  True  True  True  True  True  True  True  True  True]

    tess.plot(plot_included=True, plot_removed=True, plot_points=True)
    # Tessellation2D plotting excluded edges (red): 180
    # Tessellation2D plotting included edges (green): 180
    # Tessellation2D plotting points: 100
    ```

    ![2D tessellation example plot](2d.PNG)

=== "3D Example"

    ``` py
    import numpy as np

    from tessellation import Tessellation

    # sample points near the equator of a sphere
    rng = np.random.default_rng(0)
    phi = rng.uniform(-np.pi, np.pi, 200)
    theta = rng.uniform(-np.pi/8, np.pi/8, 200)
    points = np.transpose([
        np.cos(theta) * np.cos(phi),
        np.cos(theta) * np.sin(phi),
        np.sin(theta),
    ])
    points += rng.normal(0, 0.05, points.shape)

    # apply tessellation algorithm
    tess = Tessellation(points)

    print(tess)
    # Tessellation3D[measure=0.26829672434602075]
    print(tess.measure)
    # 0.26829672434602075
    print(tess.points)
    # [[ 0.63512524  0.7215625  -0.11458621]
    #  [ 0.12474032 -0.88283795 -0.2977479 ]
    #  ...
    #  [-0.97540924  0.09755876 -0.03806598]
    #  [ 0.82571336  0.55325174 -0.1681618 ]]
    print(tess.tri.simplices)
    # [[ 23  42  90  41]
    #  [192  23  42  41]
    #  ...
    #  [ 95 177  38  90]
    #  [ 95 103  38  90]]
    print(tess.mask)
    # [False False  True  True  True  True  True  True  True  True  True False
    #  False False False False False  True  True  True  True  True  True  True
    #  ...
    #   True  True  True  True  True  True  True  True  True  True  True  True
    #   True  True  True]

    tess.plot(plot_included=True, plot_removed=True, plot_points=True)
    # Tessellation3D plotting in/ex edges (blue): 99
    # Tessellation3D plotting excluded edges (red): 42
    # Tessellation3D plotting included edges (green): 1095
    # Tessellation3D plotting points: 200
    ```

    ![3D tessellation example plot](3d.PNG)
