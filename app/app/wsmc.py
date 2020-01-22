import multiprocessing as mp
import os
import sys
import timeit
import math
from collections import OrderedDict
import datetime
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


def decode_field(field, data):
    decoded = int.from_bytes(data, byteorder="big", signed=True)

    if field == "station_id":
        return decoded

    if field == "timestamp":
        return datetime.datetime.utcfromtimestamp(decoded)

    if field == "rainfall":
        return decoded / 100

    if field == "wind_direction":
        return decoded

    if field == "events" or field == "null_indication":
        return format(decoded, "b")

    if field in ("temperature",
                 "dew_point",
                 "air_pressure",
                 "sea_air_pressure",
                 "visibility",
                 "air_speed",
                 "snowfall",
                 "cloud_pct"):
        return decoded / 10

    else:
        raise ValueError("Unnown field")


def decode_measurement(bindata):
    measurement = OrderedDict()
    i = 0

    for field, bytecount in PROTOCOL_FORMAT_BC.items():
        measurement[field] = decode_field(field, bindata[i:i+bytecount])
        i += bytecount

    return measurement


def search_by_field(bindata, sfield, value, rfield=None, skip=None):
    datalen = len(bindata)
    field_startbyte = PROTOCOL_FORMAT_BS[sfield]
    bytecount = PROTOCOL_FORMAT_BC[sfield]

    i = field_startbyte
    skipcount = 0

    while i < datalen:
        svalue = bindata[i:i + bytecount]
        decoded = decode_field(sfield, svalue)

        if decoded == value:

            if skip and skipcount < skip:
                skipcount += 1
                i += MEASUREMENT_BYTE_COUNT
                continue

            skipcount = 0

            m_startbyte = i - field_startbyte

            if rfield:
                """ Return decoded value for field """
                m_field_startbyte = m_startbyte + PROTOCOL_FORMAT_BS[rfield]
                field_data = bindata[m_field_startbyte:m_field_startbyte + PROTOCOL_FORMAT_BC[rfield]]
                yield decode_field(rfield, field_data)
            else:
                """ Return decoded measurement """
                measurement_data = bindata[m_startbyte:m_startbyte + MEASUREMENT_BYTE_COUNT]
                yield decode_measurement(measurement_data)

        i += MEASUREMENT_BYTE_COUNT


def read_wsmc_file(filepath, bytecount=None):
    with open(filepath, "rb") as f:
        if bytecount:
            return f.read(bytecount)
        else:
            return f.read()


def find_all_stations_by_id_return_measurement(data):
    measurements = list(search_by_field(data, "station_id", 743700))
    # print("measurements:", len(measurements))
    print(measurements[0])


def find_all_stations_by_id_return_only_temperatures(data):
    temperatures = list(search_by_field(data, "station_id", 743700, rfield="temperature"))
    print("temperatures:", len(temperatures))


def find_all_stations_by_id_return_only_temperatures_and_skip_60(data):
    temperatures = list(search_by_field(data, "station_id", 743700, rfield="temperature", skip=50))
    print("temperatures:", len(temperatures))


def search_by_field_to_list(sharedlist, data, sfield, value, rfield=None, skip=None):
    temperatures = list(search_by_field(data, sfield, value, rfield))
    sharedlist.append(len(temperatures))


def read_test_wsmc_file():
    filepath = os.path.join(const.MEASUREMENTS_DIR, "pizza.wsmc")
    return read_wsmc_file(filepath, ACTUAL_CHUNK_SIZE)


def search_by_field_threaded(pool, cpucount, data, workerbytes):
    manager = mp.Manager()
    sharedlist = manager.list()
    i = 0
    jobs = []

    for p in range(cpucount):
        workerdata = data[i:i + workerbytes]
        p = pool.apply_async(
            search_by_field_to_list,
            (sharedlist, workerdata, "station_id", 743700, "temperature")
        )
        jobs.append(p)
        i += workerbytes

    [job.wait() for job in jobs]

    print("temperatures:", sum(sharedlist))


def iterate_dataset_left(data, fieldname):
    """ Each iteration the value of the given fieldname is yielded. """
    i = len(data)
    while i > 0:
        measurementaddr = (i - MEASUREMENT_BYTE_COUNT)
        yield data[measurementaddr:measurementaddr + MEASUREMENT_BYTE_COUNT]
        i -= MEASUREMENT_BYTE_COUNT


def filter_measurements_by_field(data, fieldname, value):
    fieldaddr = PROTOCOL_FORMAT_BS[fieldname]
    field_bc = PROTOCOL_FORMAT_BC[fieldname]

    for measurementbytes in iterate_dataset_left(data, "station_id"):
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        decoded = decode_field(fieldname, bytevalue)

        if decoded == value:
            yield measurementbytes


def filter_measurements_by_timestamp(data, station_id, dt1, dt2):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]

    for measurementbytes in filter_measurements_by_field(data, "station_id", station_id):
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)
        if dt1 <= timestamp <= dt2:
            yield decode_measurement(bytevalue)


def iterate_dataset_left_to_list(sharedlist, data, fieldname):
    temperatures = list(iterate_dataset_left(data, fieldname))
    sharedlist.append(len(temperatures))


def iterate_dataset_left_threaded(pool, cpucount, data, workerbytes, fieldname):
    manager = mp.Manager()
    sharedlist = manager.list()
    i = 0
    jobs = []

    for p in range(cpucount):
        workerdata = data[i:i + workerbytes]
        p = pool.apply_async(
            iterate_dataset_left_to_list,
            (sharedlist, workerdata, fieldname)
        )
        jobs.append(p)
        i += workerbytes

    [job.wait() for job in jobs]

    print("temperatures:", sum(sharedlist))


if __name__ == "__main__":
    data = read_test_wsmc_file()
    datalength = len(data)

    if datalength % MEASUREMENT_BYTE_COUNT != 0:
        raise Exception("wsmc file is corrupt")

    # Should return 8 measurements
    dt1 = datetime.datetime(2020, 1, 21, 14, 56, 38)
    dt2 = datetime.datetime(2020, 1, 21, 14, 56, 45)
    print(timeit.timeit(
        "print(len(list(filter_measurements_by_timestamp(data, 743700, dt1, dt2))))",
        number=1,
        globals=globals()
    ))

    # print(timeit.timeit(
    #     "print(len(list(filter_measurements_by_field(data, 'station_id', 743700))))",
    #     number=1,
    #     globals=globals()
    # ))

    # print(timeit.timeit(
    #     "print(len(list(iterate_dataset_left(data, 'station_id'))))",
    #     number=1,
    #     globals=globals()
    # ))

    # cpucount = mp.cpu_count()
    # with mp.Pool(cpucount) as pool:
    #     measurements = int(datalength / MEASUREMENT_BYTE_COUNT)
    #     if measurements % cpucount != 0:
    #         raise Exception("Can not divide work to CPUs")
    #
    #     measurements_per_worker = int(measurements / cpucount)
    #     workerbytes = measurements_per_worker * MEASUREMENT_BYTE_COUNT
    #
    #     print(timeit.timeit(
    #         "iterate_dataset_backwards_threaded(pool, cpucount, data, workerbytes, 'temperature')",
    #         number=1,
    #         globals=globals()
    #     ))

    # cpucount = mp.cpu_count()
    # with mp.Pool(cpucount) as pool:
    #     measurements = int(datalength / MEASUREMENT_BYTE_COUNT)
    #     if measurements % cpucount != 0:
    #         raise Exception("Can not divide work to CPUs")
    #
    #     measurements_per_worker = int(measurements / cpucount)
    #     workerbytes = measurements_per_worker * MEASUREMENT_BYTE_COUNT
    #
    #     print(timeit.timeit(
    #         "search_by_field_threaded(pool, cpucount, data, workerbytes)",
    #         number=1,
    #         globals=globals()
    #     ))

    # print("Find all stations by ID, return temperatures")
    # print(timeit.timeit(
    #     "find_all_stations_by_id_return_only_temperatures(data)",
    #     number=1,
    #     globals=globals()
    # ))

    # print("Find all stations by ID, return measurements")
    # print(timeit.timeit(
    #     "find_all_stations_by_id_return_measurement(data)",
    #     number=1,
    #     globals=globals()
    # ))

# def _retrieve_measurements_from_fs(station_id=None, dt1=None, dt2=None):
#     files = os.listdir(const.MEASUREMENTS_DIR)
#     files.sort(key=lambda name: int(re.sub('\D', '', name)))
#     files = list((name.split(".wsmc")[0] for name in files if ".wsmc" in name))
#     print(files)
