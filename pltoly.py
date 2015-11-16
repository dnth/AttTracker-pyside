import plotly.plotly as py
from plotly.graph_objs import *

data = Data([
    Scatter(
        x=[1, 2, 3],
        y=[1, 3, 1]
    )
])
py.iplot(data, filename='privacy', sharing='secret')
py.iplot(data, filename='privacy', sharing='secret')