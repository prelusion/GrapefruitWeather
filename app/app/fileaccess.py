import csv
import os
from copy import deepcopy

from flask_login import UserMixin

from app import util, const

_stations_data = None
_tracks_data = None
_countries_data = None
_timezones_data = None
_users_data = None
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

    return deepcopy(_stations_data)


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
                })
    return _timezones_data


def generate_track_distance_cache(data, track_id):
    os.makedirs(const.TRACK_CACHE_DIR, exist_ok=True)
    file_path = os.path.join(const.TRACK_CACHE_DIR, str(track_id) + ".csv")
    with open(file_path, 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerow(("id", "distance"))
        for row in data:
            wr.writerow(row)


def get_track_distances(track_id):
    global _distance_data

    if track_id not in _distance_data:
        _distance_data[track_id] = {}
        with open(const.TRACK_CACHE_DIR + "/" + str(track_id) + ".csv") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _distance_data[track_id][row[0]] = row[1]
    return _distance_data[track_id]


def get_user(user_id=None, username=None):
    global _users_data

    if not _users_data:

        _users_data = {}

        with open(os.path.join(const.DATA_DIR, "users.csv")) as f:
            user_dict = util.csv_to_array_of_dicts(f)

        for user in user_dict:
            new_user = UserMixin()
            new_user.id = user["id"]
            new_user.username = user["name"]
            new_user.password = user["password"]

            _users_data[new_user.get_id()] = new_user

    if user_id is None:
        for user in _users_data.values():
            if user.username == username:
                return user
    if user_id in _users_data:
        return _users_data[user_id]
    else:
        return False
