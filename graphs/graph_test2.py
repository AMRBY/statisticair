import matplotlib.pyplot as plt

# Sample data
x = [1, 2, 3, 4, 5]
y = [10, 20, 25, 30, 40]

# Create the plot
plt.plot(x, y)

# Add labels and title
plt.xlabel('x-axis')
plt.ylabel('y-axis')
plt.title('Sample Graph')

# Save the plot as a PNG file
plt.savefig('plot.png')

# Show the plot
plt.show()
