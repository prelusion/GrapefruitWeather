from collections import OrderedDict
import os
from app import const
import math
import timeit

PREFERRED_CHUNK_SIZE = 104857600  # +- 100 MB

# Byte count for each field within a measurement
PROTOCOL_FORMAT_BC = OrderedDict({
    "station_id": 3,
    "timestamp": 4,
    "null_indication": 2,
    "temperature": 3,
    "dew_point": 3,
    "air_pressure": 3,
    "sea_air_pressure": 3,
    "visibility": 2,
    "air_speed": 2,
    "rainfall": 3,
    "snowfall": 2,
    "events": 1,
    "cloud_pct": 2,
    "wind_direction": 2,
})

# Starting byte for each field within a measurement
PROTOCOL_FORMAT_BS = OrderedDict({
    "station_id": 0,
    "timestamp": 3,
    "null_indication": 7,
    "temperature": 9,
    "dew_point": 12,
    "air_pressure": 15,
    "sea_air_pressure": 18,
    "visibility": 21,
    "air_speed": 23,
    "rainfall": 25,
    "snowfall": 28,
    "events": 30,
    "cloud_pct": 31,
    "wind_direction": 33,
})

MEASUREMENT_BYTE_COUNT = sum(PROTOCOL_FORMAT_BC.values())
CHUNKS = math.trunc(PREFERRED_CHUNK_SIZE / MEASUREMENT_BYTE_COUNT)
ACTUAL_CHUNK_SIZE = CHUNKS * MEASUREMENT_BYTE_COUNT


def decode_wsmc(bindata):
    binarydatalen = len(bindata)
    i = 0

    while i < binarydatalen:
        measurement = OrderedDict()

        for name, bytecount in PROTOCOL_FORMAT_BC.items():

            if i > binarydatalen or i + bytecount > binarydatalen:
                return

            bytesout = bindata[i:i + bytecount]
            converted = int.from_bytes(bytesout, byteorder="big", signed=True)

            if name in ("events", "null_indication"):
                converted = format(converted, "b")

            if name == "rainfall":
                converted = converted / 100

            if name in ("temperature",
                        "dew_point",
                        "air_pressure",
                        "sea_air_pressure",
                        "visibility",
                        "air_speed",
                        "snowfall",
                        "cloud_pct"):
                converted = converted / 10

            measurement[name] = converted
            i += bytecount

        yield measurement


def decode_wsmc_measurement(bindata):
    measurement = OrderedDict()
    i = 0

    for name, bytecount in PROTOCOL_FORMAT_BC.items():

        bytesout = bindata[i:i + bytecount]
        converted = int.from_bytes(bytesout, byteorder="big", signed=True)

        if name in ("events", "null_indication"):
            converted = format(converted, "b")

        if name == "rainfall":
            converted = converted / 100

        if name in ("temperature",
                    "dew_point",
                    "air_pressure",
                    "sea_air_pressure",
                    "visibility",
                    "air_speed",
                    "snowfall",
                    "cloud_pct"):
            converted = converted / 10

        measurement[name] = converted
        i += bytecount

    return measurement


def decode_field(field, bindata):
    bytesout = bindata[0:PROTOCOL_FORMAT_BC[field]]
    decoded = int.from_bytes(bytesout, byteorder="big", signed=True)

    if field in ("events", "null_indication"):
        decoded = format(decoded, "b")

    if field == "rainfall":
        decoded = decoded / 100

    if field in ("temperature",
                 "dew_point",
                 "air_pressure",
                 "sea_air_pressure",
                 "visibility",
                 "air_speed",
                 "snowfall",
                 "cloud_pct"):
        decoded = decoded / 10

    return decoded


def search_by_field(bindata, field, value):
    datalen = len(bindata)
    startbyte = PROTOCOL_FORMAT_BS[field]
    bytecount = PROTOCOL_FORMAT_BC[field]

    i = startbyte

    while i < datalen:
        rvalue = bindata[i:i + bytecount]
        decoded = decode_field(field, rvalue)

        if decoded == value:
            measurementdata = bindata[i:i + MEASUREMENT_BYTE_COUNT]
            measurement = decode_wsmc_measurement(measurementdata)
            yield measurement

        i += MEASUREMENT_BYTE_COUNT


def read_wsmc_file(filepath, bytecount=None):
    with open(filepath, "rb") as f:
        if bytecount:
            return f.read(bytecount)
        else:
            return f.read()


def find_all_stations_by_id_not_decoding_all_measurements():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    data = read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)
    measurements = list(search_by_field(data, 'station_id', 743700))
    print("measurements:", len(measurements))


def find_all_stations_by_id_decoding_all_measurements():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    data = read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)
    measurements = []
    for measurement in decode_wsmc(data):
        if measurement["station_id"] == 743700:
            measurements.append(measurement)
    print("measurements:", len(measurements))


if __name__ == "__main__":
    print("Alle stations met specifiek ID zoeken waarbij ik steeds station ID vergelijk en dan de bytes skip naar de volgende meting.")
    print(timeit.timeit("find_all_stations_by_id_not_decoding_all_measurements()", number=1, setup="from __main__ import find_all_stations_by_id_not_decoding_all_measurements"))
    print("Alle stations met specifiek ID zoeken waarbij ik steeds de meting decode, en dan het station ID vergelijk.")
    print(timeit.timeit("find_all_stations_by_id_decoding_all_measurements()", number=1, setup="from __main__ import find_all_stations_by_id_decoding_all_measurements"))
















#
# def find_measurements_by_station_id(station_id=None):
#     filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
#
#     print("start reading")
#     data = read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)
#     print("start decoding")
#     measurements = list(decode_wsmc(data))
#     print("measurements:", measurements)
#     # for measurement in decode_wsmc(data):
#     #     print("measurement:", measurement)
#     # print(data)


# def _retrieve_measurements_from_fs(station_id=None, dt1=None, dt2=None):
#     files = os.listdir(const.MEASUREMENTS_DIR)
#     files.sort(key=lambda name: int(re.sub('\D', '', name)))
#     files = list((name.split(".wsmc")[0] for name in files if ".wsmc" in name))
#     print(files)