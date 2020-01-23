import csv
import os

from app import const

_stations_data = None


def get_stations_db():
    global _stations_data

    if not _stations_data:
        _stations_data = []
        with open(os.path.join(const.DATA_DIR, "stations.csv")) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _stations_data.append({
                    "id": row[0],
                    "name": row[1],
                    "country-id": row[2],
                    "latitude": row[3],
                    "longitude": row[4],
                    "height": row[5],
                    "timezone": row[6]
                })

    return _stations_data
