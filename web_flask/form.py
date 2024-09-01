#!/usr/bin/python3
"""
starts a Flask web application
"""
import subprocess
import os
from models.storage import storage
from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def index():
    return 'Hello Everybody!'

@app.route('/form', methods=['GET', 'POST'], strict_slashes=False)
def form():
    flights = None
    count = None
    distances = None
    filtre = {}
    a = storage()
    if request.method == 'POST':
        a.date_from = request.form['date_from']
        a.date_to = request.form['date_to']
        a.origin = request.form['from']
        a.destination = request.form['to']
        a.flight_id = request.form['flight_id']
    elif session.get('date_from') and session.get('date_to'):
        a.date_from = session.get('date_from')
        a.date_to = session.get('date_to')
        a.origin = session.get('origin')
        a.destination = session.get('destination')
        a.flight_id = session.get('flight_id')
 
    filtre = {'From': a.origin, 'To': a.destination, 'Flight_id': a.flight_id, 'Date_from': a.date_from, 'Date_to': a.date_to}
    flights = a.show_flights()
    count = a.count()
    distances = a.show_distances(flights)
    session['date_from'] = a.date_from
    session['date_to'] = a.date_to
    session['origin'] = a.origin
    session['destination'] = a.destination
    session['flight_id'] = a.flight_id
    redirect(url_for('graph'))
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
    from models.graph import pie_graph, bar_graph
    a = storage()
    if request.method == 'POST':
        a.date_from = request.form['date_from']
        a.date_to = request.form['date_to']
        a.origin = request.form['from']
        a.destination = request.form['to']
        a.flight_id = request.form['flight_id']
    elif session.get('date_from') and session.get('date_to'):
        a.date_from = session.get('date_from')
        a.date_to = session.get('date_to')
        a.origin = session.get('origin')
        a.destination = session.get('destination')
        a.flight_id = session.get('flight_id')
 
    filtre = {'Date_from': a.date_from, 'Date_to': a.date_to}
    flights = a.show_flights()
    #print(f"flights={flights}")
    count = a.count()
    distances = a.show_distances(flights)
    labels, sizes = a.companies()
    days = list(a.daily_kea().keys())
    keas = list(a.daily_kea().values())
    if flights != ():
        pie_graph(sizes, labels)
        bar_graph(days, keas)

    session['date_from'] = a.date_from
    session['date_to'] = a.date_to
    session['origin'] = a.origin
    session['destination'] = a.destination
    session['flight_id'] = a.flight_id
    redirect(url_for('form'))
    return render_template('graph.html', days=days, labels=labels, flights=flights, filtre=filtre, count=count, distances=distances)
    
@app.route('/import', methods=['GET', 'POST'], strict_slashes=False)
def import_data():
    result = None
    di = None
    fl = None
    kea = None
    a = storage()
    if request.method == "POST":
        record = request.files['file']
        record_path = os.path.join("record/", record.filename)
        record.save(record_path)
        #abso = os.path.abspath(__file__)
        acb_name = 'ACB' + record.filename.split('.')[2] + record.filename.split('.')[3] + record.filename.split('.')[4]
        acb_path = os.path.join("record/", acb_name)
        try:
            result = subprocess.run(['bash', "commands_awk.sh", record_path, acb_path], check=True, text=True, capture_output=True)
            std = result.stdout
            di, fl, kea = a.upload(acb_path)
        except subprocess.CalledProcessError as e:
            std = e.stderr
    return render_template('import.html', di=di, fl=fl, kea=kea)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
