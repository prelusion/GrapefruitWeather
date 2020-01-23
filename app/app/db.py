from copy import deepcopy
from geopy import distance
from app import fileaccess
from app import wsmc
from app.const import RACING_TRACKS
from app.util import limit_and_offset


def get_racing_tracks(track_id=None, name=None, city=None, country=None, limit=None, offset=None):
    racing_tracks = deepcopy(RACING_TRACKS)

    if track_id is not None:
        racing_tracks = list(filter(lambda track: track["id"] == int(track_id), racing_tracks))
    if name is not None:
        racing_tracks = list(filter(lambda track: track["title"].lower() == name.lower(), racing_tracks))
    if city is not None:
        racing_tracks = list(
            filter(lambda track: track["city"] is not None and track["city"].lower() == city.lower(),
                   racing_tracks))
    if country is not None:
        racing_tracks = list(filter(lambda track: track["country"].lower() == country.lower(), racing_tracks))

    racing_tracks = limit_and_offset(racing_tracks, limit, offset)

    return True, racing_tracks


def get_stations(station_id=None,
                 longitude=None,
                 latitude=None,
                 radius=None,
                 country=None,
                 limit=50,
                 timezone=None,
                 offset=None
                 ):
    stations = deepcopy(fileaccess.get_stations_db())

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
            station["distance"] = round(
                distance.distance([float(station["latitude"]), float(station["longitude"])],
                                  target_location).km)

    if longitude is not None and latitude is not None:
        stations.sort(key=lambda station: station["distance"])

    if longitude is not None and latitude is not None and radius is not None:
        stations = list(filter(lambda station: station["distance"] < float(radius), stations))

    stations = limit_and_offset(stations, limit, offset)

    return True, stations


def get_most_recent_air_pressure_average(station_ids, seconds, interval):
    rawdata = wsmc.read_test_file()
    measurementbytes_generator = wsmc.iterate_dataset_left(rawdata)
    measurementbytes_generator = wsmc.filter_measurements_by_field(
        measurementbytes_generator, "station_id", station_ids)
    measurement_generator = wsmc.filter_most_recent_measurements_group_by_interval(
        measurementbytes_generator, seconds, interval)
    avg_temperatures = list(
        wsmc.get_most_recent_measurements_averages("temperature", measurement_generator))
    return avg_temperatures


def get_measurements(station_id=None, dt1=None, dt2=None, limit=None, offset=None):
    pass


def get_average_measurements(stations, interval, dt1, dt2):
    """ Returns an array of measurements averaged by the following conditions:
        - All measurements within each interval are averaged per station
        - The averages for each station are taken as an average per interval

        This results in an array of averages per interval which are averages
        of multiple stations and multiple measurements.

        :returns [{ "timestamp": "", "field": "", "value": ""], total
    """

    """
    PSEUDOCODE:
    
    # Get average per interval for each station
    station_results = []
    for station_id in stations:
        measurements = _retrieve_measurements_from_fs(station_id, dt1, dt2)
        measurements_per_interval = split_by_interval(measurements)
        average_per_interval = map(avg(measurements), measurements_per_interval)
        station_results.append(average_per_interval)
    
    # Get average per interval of all stations
    station_count = len(stations)
    interval_count = len(stations[0])
    averages = []
    for i in range(interval_count):
        value = 0
        for j in range(station_count):
            value += station_results[j][i]
        averages.append(value / station_count)
    
    return averages
    """
