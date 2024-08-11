import matplotlib.pyplot as plt

# Sample data
labels = ['Apple', 'Banana', 'Cherry', 'Date']
sizes = [30, 15, 25, 30]
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
explode = (0.1, 0, 0, 0)  # explode the 1st slice (i.e. 'Apple')

# Create the pie chart
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=140)

plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('Sample Pie Chart')
plt.savefig('pie_chart.png')
plt.show()
