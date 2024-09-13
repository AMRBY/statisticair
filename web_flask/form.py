#!/usr/bin/python3
"""
starts a Flask web application
"""
import subprocess
import os
from models.storage import storage
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
    flights = a.show_all()
    count = a.count()
    session['date_from'] = a.date_from
    session['date_to'] = a.date_to
    session['origin'] = a.origin
    session['destination'] = a.destination
    session['flight_id'] = a.flight_id
    redirect(url_for('graph'))
    return render_template('index.html', flights=flights, filtre=filtre, count=count)

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
    count = a.count()
    labels, sizes = a.companies()
    days = list(a.daily_kea().keys())
    keas = list(a.daily_kea().values())
    if labels != [] and sizes != []:
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
    fix_msg = ""
    file_msg = ""
    result = None
    di = None
    fl = None
    kea = None
    a = storage()
    if request.method == "POST":
        record = request.files['file']
        fix_name = request.form.get('fix_name')
        fix_airport = request.form.get('fix_airport')
        lat_deg = request.form.get('lat_deg')
        lat_min = request.form.get('lat_min')
        lat_sec = request.form.get('lat_sec')
        lon_deg = request.form.get('lon_deg')
        lon_min = request.form.get('lon_min')
        lon_sec = request.form.get('lon_sec')
        if record.filename == '':       
            if fix_name and fix_airport and lat_deg and lat_min and lat_sec and lon_deg and lon_min and lon_sec:
                s = storage()
                fix_msg = s.upload_fix(fix_name, fix_airport, lat_deg, lat_min, lat_sec, lon_deg, lon_min, lon_sec)

            else:
                file_msg = "Please, choose a file or fill all fixpoint/airport informations!"
        else:
            if fix_name and fix_airport and lat_deg and lat_min and lat_sec and lon_deg and lon_min and lon_sec:
                s = storage()
                fix_msg = s.upload_fix(fix_name, fix_airport, lat_deg, lat_min, lat_sec, lon_deg, lon_min, lon_sec)
            try:
                missed_fix = a.upload(record)
                if missed_fix != "":
                    file_msg = missed_fix
                else:
                    file_msg = "File loaded successfully!"
            except Exception as e:
                file_msg = "Error found in file!" 
    return render_template('import.html', fix_msg=fix_msg, file_msg=file_msg)

@app.route('/api', methods=['GET'], strict_slashes=False)
def api():
    s = storage()
    flights = s.show_flights()
    results = s.to_dict(flights)
    return jsonify(results)

@app.route('/api/<int:f_id>', methods=['GET'], strict_slashes=False)
def api_by_id(f_id):
    s = storage()
    flights = s.show_flights()
    results = s.to_dict(flights)
    if f_id:
        for flight in results:
            if flight["id"] == f_id:
                return jsonify(flight)
    return jsonify({"Error":"id does not exist"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
