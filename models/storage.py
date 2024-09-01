#!/usr/bin/python3

import subprocess
import MySQLdb
from sys import argv
import json
from datetime import datetime, timedelta
from models.flight import flight


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

class storage(DateTimeEncoder, flight):

    date_from = None
    date_to = None

    def __init__(self, flight_id=None, origin=None, destination=None, arrived_at=None, route=None):
        flight.__init__(self, flight_id, origin, destination, arrived_at, route)

    def upload(self, acb_path):
        # save acb to db
        calcul = None
        db_path = '/var/lib/mysql-files/'
        acb_name = db_path + acb_path.split('/')[-1]
        command1 = ['cp', acb_path, db_path]
        command2 = ['chown', 'mysql:mysql', acb_name]
        result1 = subprocess.run(command1, check=True, text=True, capture_output=True)
        result2 = subprocess.run(command2, check=True, text=True, capture_output=True)
        max_id_query = "SELECT MAX(id) from flights;"
        upload_query = "LOAD DATA INFILE %s INTO TABLE flights FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' (arrived_at, flight_id, origin, destination, route);"
        uploaded_query = "SELECT * FROM flights WHERE id > %s"
        self.cur.execute("USE kpi;")
        self.cur.execute(max_id_query)
        max_id = self.cur.fetchone()[0]
        self.cur.execute(upload_query, (acb_name,))
        self.conn.commit()
        self.cur.execute(uploaded_query, (max_id,))
        uploaded_rows = self.cur.fetchall()
        flights = self.to_dict(uploaded_rows)
        di, fl, kea = self.calculator(flights)
        return (di, fl, kea)
        
        """
        record = request.files['file']
        record_path = os.path.join("record/", record.filename)
        record.save(record_path)
        acb_name = 'ACB' + record.filename.split('.')[2] + record.filename.split('.')[3] + record.filename.split('.')[4]
        acb_path = os.path.join("record/", acb_name)
        try:
            result = subprocess.run(['bash', "commands_awk.sh", record_path, acb_path], check=True, text=True, capture_output=True)
            std = result.stdout
        except subprocess.CalledProcessError as e:
            std = e.stderr
        """
    def delete(self):
        # need "DELETE" query to delete a flight from db
        pass

    def show_flights(self):
        #base_query = "SELECT * FROM flights JOIN distances ON flights.id=distances.id_flight WHERE 1=1 "
        base_query = "SELECT * FROM flights WHERE 1=1 "
        params = []
        if self.flight_id:
            base_query += "AND flight_id LIKE %s"
            params.append(f"{self.flight_id}%")
        if self.origin:
            base_query += "AND origin LIKE %s"
            params.append(f"{self.origin}%")
        if self.destination:
            base_query += "AND destination LIKE %s"
            params.append(f"{self.destination}%")
        if self.route:
            base_query += "AND route LIKE %s"
            params.append(f"{self.route}%")
        if self.date_from and self.date_to:
            base_query += "AND DATE(arrived_at) BETWEEN %s AND %s"
            params.append(self.date_from)
            params.append(self.date_to)

        self.cur.execute(base_query, params)
        query_rows = self.cur.fetchall()
        return query_rows

    def to_dict(self, query_rows):
        list_dict = []
        #query_rows = None
        #query_rows = self.show_flights()
        if query_rows is not None:
            for row in query_rows:
                flight_dict = {}
                flight_dict['id'] = row[0]
                flight_dict['flight_id'] = row[1]
                flight_dict['origin'] = row[2]
                flight_dict['destination'] = row[3]
                flight_dict['arrived_at'] = row[4]
                flight_dict['route'] = row[5]
                list_dict.append(flight_dict)
            return list_dict

    def to_json(self):
        query_rows = None
        query_rows = self.show_flights()
        if query_rows is not None:
            json_output = json.dumps(query_rows, cls=DateTimeEncoder)
        return json_output 
            
    def count(self):
        nb_flights = self.show_flights()
        return len(nb_flights)

    def calculator(self, list_of_dict):
        di = None
        fl = None
        kea = None
        #flights = self.show_flights()
        #to_dict = self.to_dict()
        for flights in list_of_dict:
            f = flight()
            f.flight_id = flights['flight_id']
            f.origin = flights['origin']
            f.destination = flights['destination']
            f.arrived_at = flights['arrived_at']
            f.route = flights['route']
            gm = f.gm(f.decimal())
            di = f.direct(gm)
            fl = f.flown(gm)
            kea = f.kea(di, fl)
            #print(di, fl, kea)
            f.to_db(di, fl, kea)
        return (di, fl, kea)

    def show_distances(self, flights):
        distances = []
        for flight in flights:
            base_query = f"SELECT flights.flight_id, distances.direct, distances.flown FROM distances JOIN flights ON distances.id_flight=flights.id WHERE distances.id_flight=%s"
            self.cur.execute(base_query, (flight[0],))
            distances.append(self.cur.fetchall())
        return distances

    def daily_kea(self):
        kea_list = {}
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        base_query = f"SELECT SUM(distances.direct), SUM(distances.flown) FROM distances JOIN flights ON distances.id_flight=flights.id WHERE DATE(flights.arrived_at)=%s"
        current_date = date_from
        while current_date <= date_to:
            distances = ()
            self.cur.execute(base_query, (current_date,))
            distances = self.cur.fetchall()
            #print(distances)
            if distances != ((None, None),):
                kea_daily = ((distances[0][1] / distances[0][0]) - 1) * 100
                kea_list[current_date.strftime("%Y-%m-%d")] = round(kea_daily, 2)
            current_date += timedelta(days=1)
        return kea_list

    def companies(self):
        other = 0
        labels = []
        sizes = []
        base_query = f"SELECT SUBSTR(flight_id, 1, 3) AS cmp, COUNT(*) AS count FROM flights WHERE DATE(arrived_at) BETWEEN %s AND %s GROUP BY cmp HAVING count > 0 UNION SELECT 'TOTAL', COUNT(*) FROM flights WHERE DATE(arrived_at) BETWEEN %s AND %s ORDER BY count"
        self.cur.execute(base_query, (self.date_from, self.date_to, self.date_from, self.date_to))
        companies = self.cur.fetchall()
        total = companies[len(companies)-1][1]
        for i in range(0, len(companies)-1):
            percentage = companies[i][1]/total*100
            if percentage < 1:
                other += percentage
            else:
                #percentage[i[0]]= round(i[1]/total * 100, 2)
                labels.append(companies[i][0])
                sizes.append(round(companies[i][1]/total*100, 2))
        labels.append('Other')
        sizes.append(round(other, 2))
        return labels, sizes

    def close(self):
        self.cur.close()
        self.conn.close()

