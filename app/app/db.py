import os
from copy import deepcopy
from geopy import distance
import os
from app import fileaccess

DEFAULT_LIMIT = 50

RACING_TRACKS = [
    {
        "id": 1,
        "title": "MELBOURNE GRAND PRIX CIRCUIT",
        "city": "Melbourne",
        "country": "Australia",
        "latitude": -37.851710,
        "longitude": 144.973010,
    },
    {
        "id": 2,
        "title": "BAHRAIN INTERNATIONAL CIRCUIT",
        "city": None,
        "country": "Bahrain",
        "latitude": 26.031137,
        "longitude": 50.513254,
    },
    {
        "id": 3,
        "title": "HANOI CIRCUIT",
        "city": "Hanoi",
        "country": "Vietnam",
        "latitude": 21.014790,
        "longitude": 105.764399,
    },
    {
        "id": 4,
        "title": "SHANGHAI INTERNATIONAL CIRCUIT",
        "city": "Shanghai",
        "country": "China",
        "latitude": 31.339316,
        "longitude": 121.221456,
    },
    {
        "id": 5,
        "title": "CIRCUIT ZANDVOORT",
        "city": "Zandvoort",
        "country": "Netherlands",
        "latitude": 52.387459,
        "longitude": 4.544202,
    },
    {
        "id": 6,
        "title": "CIRCUIT DE BARCELONA-CATALUNYA",
        "city": None,
        "country": "Spain",
        "latitude": 41.568106,
        "longitude": 2.257192,
    },
    {
        "id": 7,
        "title": "CIRCUIT DE MONACO",
        "city": "Monte Carlo",
        "country": "Monaco",
        "latitude": 43.734434,
        "longitude": 7.421395,
    },
    {
        "id": 8,
        "title": "BAKU CITY CIRCUIT",
        "city": "Baku",
        "country": "Azerbaijan",
        "latitude": 40.372673,
        "longitude": 49.852495,
    },
    {
        "id": 9,
        "title": "CIRCUIT GILLES-VILLENEUVE",
        "city": "Montreal",
        "country": "Canada",
        "latitude": 45.503181,
        "longitude": -73.526623
    },
    {
        "id": 10,
        "title": "CIRCUIT PAUL RICARD",
        "city": None,
        "country": "France",
        "latitude": 43.251623,
        "longitude": 5.792839,
    },
    {
        "id": 11,
        "title": "RED BULL RING",
        "city": "Spielberg",
        "country": "Austria",
        "latitude": 47.220441,
        "longitude": 14.765180,
    },
    {
        "id": 12,
        "title": "SILVERSTONE CIRCUIT",
        "city": None,
        "country": "Great Britain",
        "latitude": 52.073254,
        "longitude": 1.014545,
    },
    {
        "id": 13,
        "title": "HUNGARORING",
        "city": "Budapest",
        "country": "Hungary",
        "latitude": 47.581653,
        "longitude": 19.250772,
    },
    {
        "id": 14,
        "title": "CIRCUIT DE SPA-FRANCORCHAMPS",
        "city": None,
        "country": "Belgium",
        "latitude": 50.436823,
        "longitude": 5.972007,
    },
    {
        "id": 15,
        "title": "AUTODROMO NAZIONALE MONZA",
        "city": None,
        "country": "Italy",
        "latitude": 45.621731,
        "longitude": 9.284843,
    },
    {
        "id": 16,
        "title": "MARINA BAY STREET CIRCUIT",
        "city": None,
        "country": "Singapore",
        "latitude": 1.291346,
        "longitude": 103.863867,
    },
    {
        "id": 17,
        "title": "SOCHI AUTODROM",
        "city": None,
        "country": "Russia",
        "latitude": 43.409938,
        "longitude": 39.968941,
    },
    {
        "id": 18,
        "title": "SUZUKA INTERNATIONAL RACING COURSE",
        "city": "Ino",
        "country": "Japan",
        "latitude": 34.845541,
        "longitude": 136.538941,
    },
    {
        "id": 19,
        "title": "CIRCUIT OF THE AMERICAS",
        "city": "Austin",
        "country": "United States",
        "latitude": 30.134544,
        "longitude": -97.635787,
    },
    {
        "id": 20,
        "title": "AUTÓDROMO HERMANOS RODRÍGUEZ",
        "city": "Mexico City",
        "country": "Mexico",
        "latitude": 19.403991,
        "longitude": -99.089387,
    },
    {
        "id": 21,
        "title": "AUTÓDROMO JOSÉ CARLOS PACE",
        "city": "Sao Paulo",
        "country": "Brazil",
        "latitude": -23.701195,
        "longitude": -46.697879,
    },
    {
        "id": 22,
        "title": "YAS MARINA CIRCUIT",
        "city": None,
        "country": "Abu Dhabi",
        "latitude": 24.481184,
        "longitude": 54.615285,
    },
]


def get_racing_tracks(track_id=None, name=None, city=None, country=None):
    racing_tracks = deepcopy(RACING_TRACKS)

    if track_id is not None:
        racing_tracks = list(filter(lambda track: track["id"] == int(track_id), racing_tracks))
    if name is not None:
        racing_tracks = list(filter(lambda track: track["title"].lower() == name.lower(), racing_tracks))
    if city is not None:
        racing_tracks = list(filter(lambda track: track["city"] is not None and track["city"].lower() == city.lower(), racing_tracks))
    if country is not None:
        racing_tracks = list(filter(lambda track: track["country"].lower() == country.lower(), racing_tracks))

    return True, racing_tracks


def get_stations(station_id=None, longitude=None, latitude=None, radius=None, country=None, limit=50, timezone=None):

    if limit is None:
        limit = DEFAULT_LIMIT

    stations = fileaccess.get_stations_db()

    if radius is not None and (latitude is not None or longitude is not None):
        return False, "Latitude or longitude not set."

    if station_id is not None:
        stations = list(filter(lambda station: int(station["id"]) == int(station_id), stations))

    if country is not None:
        stations = list(filter(lambda station: station["country-id"].lower() == country.lower(), stations))

    for station in stations:
        if not timezone:
            station.pop("timezone")

        if longitude is not None and latitude is not None:
            target_location = [float(latitude), float(longitude)]
            station["distance"] = round(distance.distance([float(station["latitude"]), float(station["longitude"])], target_location).km)

    if longitude is not None and latitude is not None:
        stations.sort(key=lambda station: station["distance"])

    new_stations = []
    for i in range(limit):
        new_stations.append(stations[i])
    stations = new_stations

    if longitude is not None and latitude is not None and radius is not None:
        stations = list(filter(lambda station: station["distance"] < float(radius), stations))

    return True, stations



