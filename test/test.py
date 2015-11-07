import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

def formatter(**kwargs):
    height = kwargs['height']
    return "This bar is {:0.2f} units tall".format(height)

fig, ax = plt.subplots()
ax.bar(np.arange(5), np.random.random(5), color='lightblue')
ax.margins(0.05)
ax.set_ylim(bottom=0)
datacursor(formatter=formatter, hover=True)
plt.show()