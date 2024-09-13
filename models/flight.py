#!/usr/bin/python3

from haversine import haversine, inverse_haversine, haversine_vector, Unit 
import MySQLdb
from sys import argv


class flight:
    STATI_HOST = "localhost"
    STATI_USER = "admin"
    STATI_PASSWD = "admin_pwd"
    STATI_DB = "kpi"

    def __init__(self, flight_id=None, origin=None, destination=None, arrived_at=None, route=None):
        self.conn = MySQLdb.connect(host=flight.STATI_HOST, user=flight.STATI_USER, passwd=flight.STATI_PASSWD, db=flight.STATI_DB, charset="utf8")
        self.cur = self.conn.cursor()
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.route = route
        self.arrived_at = arrived_at

    def print(self, direct, flown):
        print("flight ID is {}: direct: {}, flown: {}\n".format(self.flight_id, direct, flown))

    def decimal(self):
        fixs = [self.origin] + [self.destination] + self.route.split()
        #print(fixs[:])
        deci = []
        for i in range(2, len(fixs)):
            #if row: 
            #    print(row)
            #    deci.append(row)
            if fixs[i][0:4].isdigit() and fixs[i][5:10].isdigit() and fixs[i][4].isalpha() and fixs[i][10].isalpha():
                lat_deg = int(fixs[i][0:2])
                lat_min = int(fixs[i][2:4])
                lon_deg = int(fixs[i][5:8])
                lon_min = int(fixs[i][8:10])
                lat = round(lat_deg + (lat_min / 60), 3)
                lon = round(lon_deg + (lon_min / 60), 4)
                deci.append((lat, -lon))
                #print((lat,-lon))
            else:
                self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (fixs[i],))
                row = self.cur.fetchone()
                if row:
                    deci.append(row)
                else:
                    deci.insert(0, fixs[i])
                    #print("'{}' not found!!!".format(fixs[i]))
        #print(deci)
        return deci

    def gm(self, deci):
        if self.origin[:2] == "GM":
            self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (self.origin,))
            row = self.cur.fetchone()
            if row:
                deci = [row] + deci
            else:
                deci = [self.origin] + deci
        if self.destination[:2] == "GM":
            self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (self.destination,))
            row = self.cur.fetchone()
            if row:
                deci = deci + [row]
            else:
                deci = [self.destination] + deci
        #print(deci)
        return deci

    def direct(self, deci):
        direct_dist = -1
        #print("Direct: {:.2f} NM".format(haversine(deci[0], deci[-1], unit='nmi')))
        direct_dist = haversine(deci[0], deci[-1], unit='nmi')
        return round(direct_dist, 2)
        
    def flown(self, deci):
        flown_dist = -1
        for j in range(0, (len(deci)-1)):
            #print("{:.2f} NM".format(haversine(deci[j], deci[j+1], unit="nmi")))
            flown_dist += haversine(deci[j], deci[j+1], unit="nmi")
        #print("Flown: {:.2f} NM".format(flown_dist))
        return round(flown_dist, 2)

    def kea(self, direct_dist, flown_dist):
        kea = -1
        if direct_dist and flown_dist:
            kea = ((flown_dist / direct_dist) - 1) * 100
            #print("kea = {:.2f} %".format(kea))
        return round(kea, 2)

    def to_db(self, id_flight, direct_dist, flown_dist, kea):
        try:
            self.cur.execute("INSERT INTO distances (id_flight, direct, flown, kea) VALUES(%s, %s, %s, %s)",(id_flight, direct_dist, flown_dist, kea))
            #self.conn.commit()
        except Exception as e:
            print(e)   

    def commit(self):
        self.conn.commit()

