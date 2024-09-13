#!/usr/bin/python3

import matplotlib.pyplot as plt
#import matplotlib.rcParams as rc

def pie_graph(sizes, labels):
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    plt.figure(facecolor="#bec9ca")
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    fig = plt.axis('equal')
    plt.savefig('web_flask/static/pie_chart.png', bbox_inches='tight', dpi=200)
    plt.close()

def bar_graph(x, y):
    #plt.rcParams['figure.figsize'] = 40, 12
    #plt.xlabel('DAY')
    #plt.ylabel('KEA(%)')
    #plt.title('Bar Graph')
    fig = plt.figure()
    ax = fig.add_axes([0.1,0.3,1,0.75])
    ax.set_facecolor("#bec9ca")
    fig.set_facecolor("#bec9ca")
    plt.bar(x, y, width=0.5, color='blue')
    plt.xticks(fontsize=5, rotation=90)
    plt.yticks(fontsize=5)
    for i in range(len(x)):
        plt.text(i,y[i],y[i], fontsize=5, horizontalalignment='center', verticalalignment='bottom',)
    plt.savefig('web_flask/static/bar.png', bbox_inches='tight', dpi=300)
    plt.close()
