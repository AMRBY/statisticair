#!/usr/bin/python3

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
    #STATI_HOST = "localhost"
    #STATI_USER = "admin"
    #STATI_PASSWD = "admin_pwd"
    #STATI_DB = "kpi"

    def __init__(self, flight_id=None, origin=None, destination=None, arrived_at=None, route=None):
        #self.conn = MySQLdb.connect(host=storage.STATI_HOST, user=storage.STATI_USER, passwd=storage.STATI_PASSWD, db=storage.STATI_DB, charset="utf8")
        #self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
        flight.__init__(self, flight_id, origin, destination, arrived_at, route)

    def save(self):
        # need "INSERT" query to add a flight to DB
        pass

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
        #print(base_query, type(params[1]))
        return query_rows

    def to_dict(self):
        list_dict = []
        query_rows = None
        query_rows = self.show_flights()
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
        
    def show_distances(self, flights):
        distances = []
        for flight in flights:
            #print(flight)
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
            self.cur.execute(base_query, (current_date,))
            distances = self.cur.fetchall()
            #print(distances)
            kea_daily = ((distances[0][1] / distances[0][0]) - 1) * 100
            kea_list[current_date] = round(kea_daily, 2)
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
