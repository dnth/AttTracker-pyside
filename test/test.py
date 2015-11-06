import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
ax.plot(range(10), 'bo-')
ax.set_title('Press "e" to enable/disable the datacursor\n'
             'Press "h" to hide any annotation boxes')

dc = datacursor(keybindings=dict(hide='h', toggle='e'))

plt.show()