import matplotlib.pyplot as plt
import numpy as np

plt.style.use('_mpl-gallery')
# make data:
x = ['AAAA', 'BBBB', 'CCCC', 'DDDD']
y = [4, 5, 3, 1]
plt.xlabel('x')
plt.ylabel('y')
plt.title('Bar Graph')
#fig = plt.figure()
#fig.add_axes([0.1,0.1,0.75,0.75])
plt.bar(x, y, width=0.5, color='blue')
plt.xticks(rotation=90)
plt.savefig('bar.png', dpi=300)
