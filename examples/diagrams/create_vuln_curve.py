#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

# Create an array of 100 linearly-spaced points from 0 to 2*pi
x = np.array([17.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0, 62.0, 64.0, 66.0, 68.0, 70.0, 72.0, 74.0, 76.0, 78.0, 80.0, 82.0, 84.0, 86.0, 88.0, 90.0, 100.0])
y = np.array([0, 5.61E-05, 0.000119676, 0.000238983, 0.000451491, 0.000813598, 0.001407546, 0.002349965, 0.00380222, 0.005982567, 0.009180008, 0.01376939, 0.020226871, 0.029144114, 0.041238619, 0.05735623, 0.078460253, 0.10559985, 0.13984902, 0.182207241, 0.233455211, 0.293965791, 0.363483019, 0.440901669, 0.524104006, 0.60993153, 0.694373629, 0.773024088, 0.841778089, 0.897626918, 0.93930181, 0.967498609, 0.98454129, 0.99359009, 0.997731405, 0.999330795, 0.999839797, 1])

# Create the plot
plt.plot(x,y)
#plt.title('This is an example vulnerability curve')
plt.xlabel('0.2s gust at 10m height m/s')
plt.ylabel('Loss ratio')

# Save the figure in a separate file
plt.savefig('example_vuln_curve.png')

# Draw the plot to the screen
#plt.show()
