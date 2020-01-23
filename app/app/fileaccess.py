import csv
import os
from pprint import pprint
from app import const, util

_stations_data = None
_tracks_data = None


def get_stations():
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


def _convert_track(track):
    track["id"] = int(track["id"])
    track["latitude"] = float(track["latitude"])
    track["longitude"] = float(track["longitude"])
    return track


def get_tracks():
    global _tracks_data

    if not _tracks_data:
        with open(os.path.join(const.DATA_DIR, "tracks.csv")) as f:
            _tracks_data = util.csv_to_array_of_dicts(f)
            _tracks_data = list(map(_convert_track, _tracks_data))

    return _tracks_data
