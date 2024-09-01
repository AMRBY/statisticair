import matplotlib.pyplot as plt
import numpy as np

x = ['AAAA', 'BBBB', 'CCCC', 'DDDD']
y = [4, 5, 3, 1]
fig = plt.figure(figsize=(5,3))
ax = fig.add_axes([0.23,0.23,0.75,0.75])
ax.bar(x, y, width=0.5, color='blue')
plt.xticks(rotation=90)
#plt.rcParams['figure.figsize'] = [2, 2]
plt.savefig('bar.png', dpi=500)
