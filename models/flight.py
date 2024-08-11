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
        #self.conn = MySQLdb.connect(host="localhost", user=argv[1], passwd=argv[2], db=argv[3], charset="utf8")
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
            self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (fixs[i],))
            row = self.cur.fetchone()
            if row: 
                #print(row)
                deci.append(row)
            elif fixs[i][0:4].isdigit() and fixs[i][5:10].isdigit() and fixs[i][4].isalpha() and fixs[i][10].isalpha():
                lat_deg = int(fixs[i][0:2])
                lat_min = int(fixs[i][2:4])
                lon_deg = int(fixs[i][5:8])
                lon_min = int(fixs[i][8:10])
                lat = round(lat_deg + (lat_min / 60), 3)
                lon = round(lon_deg + (lon_min / 60), 4)
                deci.append((lat, -lon))
                #print((lat,-lon))
            else:
                deci.append('None')
                #print("'{}' not found!!!".format(fixs[i]))
        return deci

    def gm(self, deci):
        if not 'None' in deci:
            if self.origin[:2] == "GM":
                self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (self.origin,))
                row = self.cur.fetchone()
                if row:
                    deci = [row] + deci
                else:
                    deci = ['None'] + deci
            if self.destination[:2] == "GM":
                self.cur.execute("SELECT lat, lon FROM decimalfixpoints WHERE name LIKE BINARY %s", (self.destination,))
                row = self.cur.fetchone()
                if row:
                    deci = deci + [row]
                else:
                    deci = deci + ['None']
        #print(f"deci : {deci[:]}")
        return deci

    def direct(self, deci):
        direct_dist = -1
        if not 'None' in deci:
            #print("Direct: {:.2f} NM".format(haversine(deci[0], deci[-1], unit='nmi')))
            direct_dist = haversine(deci[0], deci[-1], unit='nmi')
        return round(direct_dist, 2)
        
    def flown(self, deci):
        flown_dist = -1
        if not 'None' in deci:
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

    def to_db(self, direct_dist, flown_dist, kea):
        i = 0
        self.cur.execute("SELECT id FROM flights WHERE arrived_at=%s AND route=%s",(self.arrived_at, self.route))
        row = self.cur.fetchall()
        #while row[i]:
        try:
            print(row[i], direct_dist, flown_dist, kea)
            self.cur.execute("INSERT INTO distances (id_flight, direct, flown, kea) VALUES(%s, %s, %s, %s)",(row[i], direct_dist, flown_dist, kea))
        except Exception:
            i += 1
            self.cur.execute("INSERT INTO distances (id_flight, direct, flown, kea) VALUES(%s, %s, %s, %s)",(row[i], direct_dist, flown_dist, kea))

        self.conn.commit()


"""Main Program"""
"""
def main():
    #f = flight("TEST1", "GZEA", "GMXX", "2023-12-12 12:12:12", "MABAP FOBAC CSD")
    from storage import storage
    a = storage()
    query_rows = a.show_flights("RAM")
    json = a.to_json()
    print(json)
    count = a.count()
    a.close()

main()
"""
