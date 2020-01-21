import csv
import os


def get_stations_db():
    stations = []
    print(os.getcwd())
    with open("../../DB/stations.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            stations.append(row)

    return stations