import numpy as np
import matplotlib.pyplot as plt

image = np.load('zoom1.npy')

plt.imshow(image, origin='lower', extent=(0, 4, 300, 400), aspect=4/100)
plt.show()