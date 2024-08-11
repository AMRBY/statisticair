#!/usr/bin/python3
"""
starts a Flask web application
"""
from models.storage import storage
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def index():
    return 'Hello Everybody!'

@app.route('/form', methods=['GET', 'POST'], strict_slashes=False)
def form():
    flights = None
    count = None
    distances = None
    filtre = {}
    if request.method == 'POST':
        a = storage()
        storage.date_from = request.form['date_from']
        storage.date_to = request.form['date_to']
        a.origin = request.form['from']
        a.destination = request.form['to']
        a.flight_id = request.form['flight_id']
        filtre = {'From':request.form['from'],'To':  request.form['to'], 'Flight_id': request.form['flight_id'], 'Date_from': request.form['date_from'], 'Date_to': request.form['date_to']}
        flights = a.show_flights()
        count = a.count()
        distances = a.show_distances(flights)
    return render_template('index.html', flights=flights, filtre=filtre, count=count, distances=distances)

@app.route('/graph', methods=['GET', 'POST'], strict_slashes=False)
def graph():
    flights = None
    count = None
    distances = None
    filtre = {}
    labels = []
    sizes = []
    days = []
    keas = []
    if request.method == 'POST':
        from models.graph import pie_graph, bar_graph
        a = storage()
        storage.date_from = request.form['date_from']
        storage.date_to = request.form['date_to']
        filtre = {'Date_from': request.form['date_from'], 'Date_to': request.form['date_to']}
        flights = a.show_flights()
        count = a.count()
        distances = a.show_distances(flights)
        labels, sizes = a.companies()
        days = list(a.daily_kea().keys())
        keas = list(a.daily_kea().values())
        pie_graph(sizes, labels)
        bar_graph(days, keas)
    return render_template('graph.html', labels=labels, flights=flights, filtre=filtre, count=count, distances=distances)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)

