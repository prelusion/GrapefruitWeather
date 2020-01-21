import math
import os
import timeit
from collections import OrderedDict

from app import const

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


def decode_wsmc_measurement(bindata):
    measurement = OrderedDict()
    i = 0

    for field, bytecount in PROTOCOL_FORMAT_BC.items():
        measurement[field] = decode_field(field, bindata[i:])
        i += bytecount

    return measurement


def search_by_field(bindata, sfield, value, rfield=None):
    datalen = len(bindata)
    field_startbyte = PROTOCOL_FORMAT_BS[sfield]
    bytecount = PROTOCOL_FORMAT_BC[sfield]

    i = field_startbyte

    while i < datalen:
        svalue = bindata[i:i + bytecount]
        decoded = decode_field(sfield, svalue)

        if decoded == value:
            m_startbyte = i - field_startbyte

            if rfield:
                """ Return decoded value for field """
                m_field_startbyte = m_startbyte + PROTOCOL_FORMAT_BS[rfield]
                field_data = bindata[m_field_startbyte:m_field_startbyte + PROTOCOL_FORMAT_BC[rfield]]
                yield decode_field(rfield, field_data)
            else:
                """ Return decoded measurement """
                measurement_data = bindata[m_startbyte:m_startbyte + MEASUREMENT_BYTE_COUNT]
                yield decode_wsmc_measurement(measurement_data)

        i += MEASUREMENT_BYTE_COUNT


def read_wsmc_file(filepath, bytecount=None):
    with open(filepath, "rb") as f:
        if bytecount:
            return f.read(bytecount)
        else:
            return f.read()


def find_all_stations_by_id_return_measurement():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    data = read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)

    measurements = list(search_by_field(data, "station_id", 743700))
    print("first 5 items:", measurements[:5])
    print("measurements:", len(measurements))


def find_all_stations_by_id_return_only_temperatures():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    data = read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)

    temperatures = list(search_by_field(data, "station_id", 743700, "temperature"))
    print("first 5 items:", temperatures[:5])
    print("temperatures:", len(temperatures))


if __name__ == "__main__":
    print(
        "Alle stations met specifiek ID zoeken waarbij ik steeds station ID vergelijk en dan de bytes skip naar de volgende meting. Return volledige measurement")
    print(timeit.timeit("find_all_stations_by_id_return_measurement()", number=1,
                        setup="from __main__ import find_all_stations_by_id_return_measurement"))

    print(
        "Alle stations met specifiek ID zoeken waarbij ik steeds station ID vergelijk en dan de bytes skip naar de volgende meting. Return alleen temperatuur")
    print(timeit.timeit("find_all_stations_by_id_return_only_temperatures()", number=1,
                        setup="from __main__ import find_all_stations_by_id_return_only_temperatures"))

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
