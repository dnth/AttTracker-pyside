import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor
from read_graph_tables import plot_service_daily

attendance = [['Frank', 'Jim', 'Anne'],
              ['Mary Ellen', 'Callie', 'Chris'],
              ['Janet', 'Chloe', 'Claire', 'Lisa', 'Charlie', 'Frank', 'Jim'],
              ['James', 'Anne']]
x = range(len(attendance))
y = [len(item) for item in attendance]
 
fig, ax = plt.subplots()
# ax.bar(x, y, align='center', color='lightblue')
# ax.margins(0.05)
# ax.set_ylim(bottom=0)
# 
# Using a closure to access data. Ideally you'd use a "functor"-style class.
def formatter(**kwargs):
    dist = abs(np.array(x) - kwargs['x'])
    i = dist.argmin()
    return '\n'.join(attendance[i])
# 
# datacursor(hover=True, formatter=formatter)


daily_present_list, daily_broadcast_list, days = plot_service_daily(month=11, year=2015, event_type="Dawn Service")
daily_present_rects = ax.bar(days, daily_present_list, align='center', color="g", label="Present", width=1 )
daily_braodcast_rects = ax.bar(days, daily_broadcast_list, align='center', color="yellow", bottom=daily_present_list, label="Broadcast", width=1)
datacursor(daily_present_rects, hover=False,formatter=formatter)
datacursor(daily_braodcast_rects, hover=False,formatter=formatter)
plt.show()