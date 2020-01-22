import csv
import os
from app import const


def get_stations_db():
    stations = []
    print(os.getcwd())
    with open(os.path.join(const.DATA_DIR, "stations.csv")) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            stations.append(row)

    return stations