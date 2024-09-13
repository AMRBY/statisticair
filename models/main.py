#!/usr/bin/python3
from models.storage import storage
from models.flight import flight
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt


s = storage()
f = flight()

#s.date_from = "2023-03-31"
#s.date_to = "2023-03-31"
acb_path = "/statisticair/record/.RECORD.2023.04.02"
with  open(acb_path, 'r'):
    print(s.upload(acb_path))
#flights = s.show_flights()
#to_dict = s.to_dict(flights)
#print(s.calculator(to_dict))
#dist = s.show_distances(flights)
#print(dist)
""" THIS LINES ARE USED TO CALCULATE DISTANCES AND KEA AND STORE THEM TO DB """
"""
for i in to_dict:
    #print(i)
    f.flight_id = i['flight_id']
    f.origin = i['origin']
    f.destination = i['destination']
    f.arrived_at = i['arrived_at']
    f.route = i['route']
    gm = f.gm(f.decimal())
    di = f.direct(gm)
    fl = f.flown(gm)
    kea = f.kea(di, fl)
    #print("GM= {}\nD= {}, F= {}, KEA= {}".format(gm, di, fl, kea))
    f.to_db(di, fl, kea)
"""
#s.upload("/media/sf_statisticair/record/ACB20230411")
#daily_kea = s.daily_kea()
#print(daily_kea)
#labels, sizes = s.companies()
#print(labels, sizes)
#s.calculator()
s.close()
"""
# Sample data
data = {
    'Day': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'KEA': daily_kea
}

# Create the plot
fig = px.line(data, x='x', y='y', title='Sample Graph')

# Save the plot as an HTML file
pio.write_html(fig, file='plot.html', auto_open=True)
"""
"""
# Sample data
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
#explode = (0, 0, 0, 0)  # explode the 1st slice (i.e. 'Apple')

# Create the pie chart
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=140)

plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('')
plt.savefig('pie_chart.png')
plt.show()
"""
