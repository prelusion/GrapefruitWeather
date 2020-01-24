import csv
import os
from external_tools import dataset


def get_stations_db():
    stations = []
    print(os.getcwd())
    with open("stations.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            stations.append(row)

    return stations


stations = dataset.get_data()

test = (1,2)


countries = {}
timezones = {}
ids = {}

id = 0
for station in stations:
    #if station[2] == "JAN MAYEN":
    if station[2] not in countries.values():
        countries[id] = station[2]
        ids[station[2]] = id

        id +=1


def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

with open("countries.csv", 'w', newline='') as myfile:
    wr = csv.writer(myfile)
    for key, value in countries.items():
        wr.writerow((key, value))

from timezonefinder import TimezoneFinder

tf = TimezoneFinder()
nullzones = 0;
id = 0
ids2 = {}

with open("stations.csv", 'w', newline='') as myfile:
    wr = csv.writer(myfile)
    for station in stations:
        if len(station) < 7:
            if not is_float(station[3]):
                print(station)
            timezone = tf.timezone_at(lng=float(station[4]), lat=float(station[3]))
            if timezone is None:
                continue
            if timezone not in timezones.values():
                timezones[id] = timezone
                ids2[timezone] = id
                id += 1
            wr.writerow((station[0], station[1], ids[station[2]], station[3], station[4], station[5], ids2[timezone]))
        else:
            print(station)

with open("timezones.csv", 'w', newline='') as myfile:
    wr = csv.writer(myfile)
    for key, value in timezones.items():
        wr.writerow((key, value))

test = "test"
#writer = csv.writer()

