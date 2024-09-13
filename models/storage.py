#!/usr/bin/python3

from flask import jsonify
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

    def upload_fix(self, fix_name, fix_airport, lat_deg, lat_min, lat_sec, lon_deg, lon_min, lon_sec):
        fix_name = fix_name.upper()
        select_query = "SELECT name FROM decimalfixpoints WHERE name LIKE %s"
        self.cur.execute(select_query, (fix_name,))
        fix = self.cur.fetchone()
        if fix:
            return f"'{fix[0]}' exists"
        else:
            lat_decimal = round(int(lat_deg) + int(lat_min) / 60 + int(lat_sec) / 3600, 6)
            lon_decimal = -round(int(lon_deg) + int(lon_min) / 60 + int(lon_sec) / 3600, 6)
            insert_query = "INSERT INTO decimalfixpoints (name, lat, lon) VALUES (%s, %s, %s)"
            try:
                self.cur.execute(insert_query, (fix_name, lat_decimal, lon_decimal))
                self.conn.commit()
                return f"'{fix_name}' loaded succefully!"
            except Exception:
                return f"Error found in '{fix_name}' informations!"
            
    def upload(self, record):
        # save acb to db
        import os
        import subprocess
        record_path = os.path.join("record/", record.filename)
        record.save(record_path)
        #abso = os.path.abspath(__file__)
        acb_name = 'ACB' + record.filename.split('.')[2] + record.filename.split('.')[3] + record.filename.split('.')[4]
        acb_path = os.path.join("record/", acb_name)
        result = subprocess.run(['bash', "commands_awk.sh", record_path, acb_path], check=True, text=True, capture_output=True)
        db_path = '/var/lib/mysql-files/'
        acb_name = db_path + acb_path.split('/')[-1]
        command1 = ['cp', acb_path, db_path]
        command2 = ['chown', 'mysql:mysql', acb_name]
        result1 = subprocess.run(command1, check=True, text=True, capture_output=True)
        result2 = subprocess.run(command2, check=True, text=True, capture_output=True)
        max_id_query = "SELECT MAX(id) from flights;"
        upload_query = "LOAD DATA INFILE %s INTO TABLE flights FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' (arrived_at, flight_id, origin, destination, route);"
        uploaded_query = "SELECT * FROM flights WHERE (%s IS NULL OR id > %s);"
        self.cur.execute("USE kpi;")
        self.cur.execute(max_id_query)
        max_id = self.cur.fetchone()[0]
        #print(max_id)
        self.cur.execute(upload_query, (acb_name,))
        self.conn.commit()
        self.cur.execute(uploaded_query, (max_id, max_id))
        uploaded_rows = self.cur.fetchall()
        missed_fix = ""
        flights = self.to_dict(uploaded_rows)
        di, fl, kea, missed_fix = self.calculator(flights)
        #print(di, fl, kea, missed_fix)
        if missed_fix != "":
            delete_query = "DELETE from flights WHERE (%s IS NULL OR id > %s);"
            self.cur.execute(delete_query, (max_id, max_id))
            self.conn.commit()
        self.close()
        return missed_fix
        
    def show_all(self):
        base_query = "SELECT * FROM flights JOIN distances ON flights.id=distances.id_flight WHERE 1=1 "
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


    def show_flights(self):
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
            flights_dict = self.to_dict(query_rows)
            #json_output = json.dumps(query_rows, cls=DateTimeEncoder)
            for flight in flights_dict:
                flight["arrived_at"] = flight["arrived_at"].isoformat()
            json_output = json.dumps(flights_dict)
        return json_output 
            
    def count(self):
        nb_flights = self.show_flights()
        return len(nb_flights)

    def calculator(self, list_of_dict):
        di = None
        fl = None
        kea = None
        missed_fix = ""
        deci = []
        f = flight()
        for flights in list_of_dict:
            print(flights)
            f.id = flights['id']
            f.flight_id = flights['flight_id']
            f.origin = flights['origin']
            f.destination = flights['destination']
            f.arrived_at = flights['arrived_at']
            f.route = flights['route']
            deci = f.decimal()
            if not isinstance(deci[0], str):
                gm = f.gm(deci)
                if not isinstance(gm[0], str):
                    di = f.direct(gm)
                    fl = f.flown(gm)
                    kea = f.kea(di, fl)
                    #print(f.id, di, fl, kea)
                    #f.to_db(f.id, di, fl, kea)
                    self.cur.execute("INSERT INTO distances (id_flight, direct, flown, kea) VALUES(%s, %s, %s, %s)",(f.id, di, fl, kea))
                else:
                    print("'{}': airport not found!".format(gm[0]))
                    missed_fix = f"'{gm[0]}': Airport not found!"
                    #missed_fix = gm[0]
                    self.conn.rollback()
                    break
            else:
                print("'{}': fixpoint not found!".format(deci[0]))
                missed_fix = f"'{deci[0]}': Fixpoint not found!"
                self.conn.rollback()
                break
        self.conn.commit()
        return (di, fl, kea, missed_fix)

    def show_distances(self, flights):
        distances = []
        flight_ids = tuple([flight[0] for flight in flights])
        string_fetch = ','.join(['%s'] * len(flight_ids))
        base_query = f"SELECT flights.flight_id, distances.direct, distances.flown FROM distances JOIN flights ON distances.id_flight=flights.id WHERE distances.id_flight IN ({string_fetch})"
        self.cur.execute(base_query, flight_ids)
        distances = self.cur.fetchall()
        return distances

    def daily_kea(self):
        distances = []
        kea_list = {}
        array_date = []
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        current_date = date_from
        while current_date <= date_to:
            array_date.append(current_date)
            current_date += timedelta(days=1)
        tuple_date = tuple(array_date)
        string_fetch = ','.join(['%s'] * len(tuple_date))
        base_query = f"SELECT DATE(flights.arrived_at), SUM(distances.direct), SUM(distances.flown) FROM distances JOIN flights ON distances.id_flight=flights.id WHERE DATE(flights.arrived_at) IN ({string_fetch}) GROUP BY DATE(flights.arrived_at) ORDER BY DATE(flights.arrived_at)"
        self.cur.execute(base_query, tuple_date)
        distances = self.cur.fetchall()
        if distances != ():
            for distance in distances:
                kea_daily = ((distance[2] / distance[1]) - 1) * 100
                kea_list[datetime.strftime(distance[0], "%Y-%m-%d")] = round(kea_daily, 2)
        return kea_list

    def companies(self):
        other = 0
        labels = []
        sizes = []
        base_query = f"SELECT SUBSTR(flight_id, 1, 3) AS cmp, COUNT(*) AS count FROM flights WHERE DATE(arrived_at) BETWEEN %s AND %s GROUP BY cmp HAVING count > 0 UNION SELECT 'TOTAL', COUNT(*) FROM flights WHERE DATE(arrived_at) BETWEEN %s AND %s ORDER BY count"
        self.cur.execute(base_query, (self.date_from, self.date_to, self.date_from, self.date_to))
        companies = self.cur.fetchall()
        if companies != (('TOTAL', 0),):
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

