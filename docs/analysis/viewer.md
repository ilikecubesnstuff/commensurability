<!-- invisible-code-block: python
import matplotlib.pyplot as plt
plt.ion()
-->

# Viewer

`commensurability` implements a general n-dimensional image viewer with `matplotlib`. This interactive viewer plots 2 axes of your choice, and then **scrolls** through any auxiliary axis. All of these axes (the x-axis, y-axis, and scrolling axis) can be changed within the interactive plotting window with key presses.

Although `commensurability` defines a `AnalysisViewer` class for plotting orbits alongside data, it also implements a standalone `Viewer` class that will be used in this page.

## Viewing a Custom Image

Suppose you have a 10x10x10x10 numpy array that you want to view using this viewer.

```python
import numpy as np

# define randomly for this example
data = np.random.random((10, 10, 10, 10))
```

The data along each axis spans a particular range, and the viewer requires this to be passed in as an argument. It accepts a dictionary with the axis names and limits.

```python
axlims = dict(
    x=[0, 100],
    y=[0, 100],
    z=[-5, 5],
    a=[-72, -64],
)
```

Once these are defined, the data can be viewed by creating a `Viewer` object with these parameters.

```python
from commensurability.viewer import Viewer

v = Viewer(data, axlims)
v.show()
```

## Using the Interactive Viewer

The axes of the image are mapped to the number keys on your keyboard. The example above would map `x` to `1`, `y` to `2`, and so on.

By using your scroll wheel, you can change the values for one of the axes, and view the new slice of data accordingly. The viewer has a few keyboard controls to change the axes controlled by scrolling, as well as change the x- and y-axis.

| Action | Keyboard Command |
| ------- | ------------------------- |
| Change scrolling axis | Press the number key associated with the new axis. |
| Change x-axis | Hold `Ctrl`, and press the number key associated with the new axis. |
| Change y-axis | Hold `ALt`, and press the number key associated with the new axis. |
