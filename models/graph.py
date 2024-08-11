#!/usr/bin/python3

import matplotlib.pyplot as plt

def pie_graph(sizes, labels):
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.savefig('web_flask/static/pie_chart.png', dpi=100)
    plt.close()

def bar_graph(x, y):
    plt.style.use('_mpl-gallery')
    plt.xlabel('DAY', rotation='vertical')
    plt.ylabel('KEA(%)')
    plt.title('Bar Graph')
    fig = plt.figure()
    fig.add_axes([0.2,0.2,0.75,0.75])
    plt.bar(x, y, width=0.5, color='blue')
    for i in range(len(x)):
        plt.text(i,y[i],y[i])
    fig.savefig('web_flask/static/bar.png', dpi=200)
    plt.close()
