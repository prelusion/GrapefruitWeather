import csv
import os

from app import const, util
from app.const import TRACK_CACHE_DIR
from app.util import csv_to_array_of_dicts

_stations_data = None
_tracks_data = None
_countries_data = None
_timezones_data = None
_distance_data = {}


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
    countries = get_countries()
    track["id"] = int(track["id"])
    track["latitude"] = float(track["latitude"])
    track["longitude"] = float(track["longitude"])
    track["country_id"] = int(track["country_id"])
    track["country"] = countries[track["country_id"]]["name"]
    return track


def get_tracks():
    global _tracks_data

    if not _tracks_data:
        with open(os.path.join(const.DATA_DIR, "tracks.csv"), encoding="utf-8") as f:
            _tracks_data = util.csv_to_array_of_dicts(f)
            _tracks_data = list(map(_convert_track, _tracks_data))

    return _tracks_data


def _convert_country(country):
    country["id"] = int(country["id"])
    return country


def get_countries():
    global _countries_data

    if not _countries_data:
        with open(os.path.join(const.DATA_DIR, "countries.csv")) as f:
            _countries_data = util.csv_to_array_of_dicts(f)
            _countries_data = list(map(_convert_country, _countries_data))

    return _countries_data


def get_timezones():
    global _timezones_data

    if not _timezones_data:
        _timezones_data = []
        with open(os.path.join(const.DATA_DIR, "timezones.csv")) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _timezones_data.append({
                    "id": row[0],
                    "name": row[1],
                    "offset": row[2],
                }
                )
    return _timezones_data


def generate_track_distance_cache(data, track_id):
    os.makedirs(TRACK_CACHE_DIR, exist_ok=True)
    file_path = os.path.join(TRACK_CACHE_DIR, str(track_id) + ".csv")
    with open(file_path, 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(("id", "distance"))
        for row in data:
            wr.writerow(row)


def get_track_distances(track_id):
    global _distance_data

    if track_id not in _distance_data:
        _distance_data[track_id] = {}
        with open(TRACK_CACHE_DIR + "/" + str(track_id) + ".csv") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _distance_data[track_id][row[0]] = row[1]

    return _distance_data[track_id]
