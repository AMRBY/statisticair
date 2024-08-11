#!/usr/bin/python3

from models.storage import storage
import plotly.express as px
import plotly.io as pio

# Sample data
data = {
    'x': [1, 2, 3, 4, 5],
    'y': [10, 20, 25, 30, 40]
}

# Create the plot
fig = px.line(data, x='x', y='y', title='Sample Graph')

# Save the plot as an HTML file
pio.write_html(fig, file='plot.html', auto_open=True)
