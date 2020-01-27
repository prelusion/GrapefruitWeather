
"""
Max chunksize for 8 GB RAM on Dell Inspiron 5570 with other programs running:

187,5 MB    -> Memory error
157,5 MB    -> Memory Error
150 MB      -> Fine


"""
import datetime
import math
import os
import re
import timeit
from collections import OrderedDict

from app import const
from app import util


MAX_CHUNKSIZE = 100000000  # 100 MB


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


def determine_chunksize(prefsize=500000):
    chunks = math.trunc(prefsize / MEASUREMENT_BYTE_COUNT)
    return chunks * MEASUREMENT_BYTE_COUNT


def load_all_data_test():

    data = [1]
    i = 0
    while len(data) != 0:
        del data
        data = load_data(MAX_CHUNKSIZE, offset=i)
        print("data length:", len(data))
        i += 1
        print("iteration", i)
    return i


def load_data(chunksize, offset):
    """ Loads wsmc data from the file system.

    Data is loaded backwards, which implies that the newest data is loaded first.

    :param offset: amount of chunks skipped when loading into memory
    :param chunksize: preferred amount of bytes loaded into memory
    :return: data in bytes
    """
    print("chunksize:", chunksize)
    return _load_data(determine_chunksize(chunksize), offset)


def _load_data(chunksize, offset):
    datadir = const.MEASUREMENTS_DIR
    skipbytes = offset * chunksize
    spaceleft = chunksize
    files = os.listdir(datadir)
    totaldata = []

    files = list(filter(lambda file: file.endswith(".wsmc"), files))
    files.sort(key=lambda name: int(re.sub('\D', '', name)))
    files = list((name for name in files if ".wsmc" in name))

    index = len(files) - 1
    if index < 0:
        raise ValueError(f"Unable to retrieve data with offset: {offset}")

    while index >= 0 and spaceleft > MEASUREMENT_BYTE_COUNT:
        currentfile = files[index]
        size = os.path.getsize(os.path.join(datadir, currentfile))

        if skipbytes > size:
            skipbytes -= size
        else:
            print("file:", currentfile)
            data = read_file(
                os.path.join(datadir, currentfile),
                bytecount=spaceleft, skipbytes=skipbytes)

            skipbytes = 0
            spaceleft -= len(data)
            totaldata.extend(data)

        index -= 1

    return totaldata


def read_file(filepath, bytecount=None, skipbytes=None):
    """ Reads a .wsmc file into memory.

    This function also checks that the file does not include corrupt measurements.

    :param filepath: path to .wsmc file
    :param bytecount: amount of bytes to load into memory, by default loads whole file.
    :return: data in bytes
    """
    with open(filepath, "rb") as f:
        if skipbytes:
            f.seek(skipbytes, 0)
        if bytecount:
            data = f.read(bytecount)
        else:
            data = f.read()

    if len(data) % MEASUREMENT_BYTE_COUNT != 0:
        raise Exception("wsmc file is corrupt")

    return data


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
    if field in ("temperature", "dew_point", "air_pressure", "sea_air_pressure",
                 "visibility", "air_speed", "snowfall", "cloud_pct"):
        return decoded / 10
    else:
        raise ValueError("Unnown field")


def decode_measurement(bindata):
    measurement = OrderedDict()
    i = 0

    for field, bytecount in PROTOCOL_FORMAT_BC.items():
        measurement[field] = decode_field(field, bindata[i:i + bytecount])
        i += bytecount

    return measurement


def iterate_dataset_left(data):
    """ Each iteration the value of the given fieldname is yielded. """
    i = len(data)
    while i > 0:
        measurementaddr = (i - MEASUREMENT_BYTE_COUNT)
        yield data[measurementaddr:measurementaddr + MEASUREMENT_BYTE_COUNT]
        i -= MEASUREMENT_BYTE_COUNT


def filter_by_field(measurementbytes_generator, fieldname, values):
    fieldaddr = PROTOCOL_FORMAT_BS[fieldname]
    field_bc = PROTOCOL_FORMAT_BC[fieldname]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        decoded = decode_field(fieldname, bytevalue)

        if decoded in values:
            yield measurementbytes


def filter_by_timestamp(measurementbytes_generator, dt1, dt2):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if dt1 < timestamp <= dt2:
            yield decode_measurement(bytevalue)
        elif timestamp < dt1:
            break


def filter_most_recent(measurementbytes_generator, seconds):
    fieldaddr = PROTOCOL_FORMAT_BS["timestamp"]
    field_bc = PROTOCOL_FORMAT_BC["timestamp"]
    first = None

    for measurementbytes in measurementbytes_generator:
        bytevalue = measurementbytes[fieldaddr:fieldaddr + field_bc]
        timestamp = decode_field("timestamp", bytevalue)

        if not first:
            first = timestamp

        if timestamp < first - datetime.timedelta(seconds=seconds):
            break

        yield measurementbytes


def group_by_timestamp(measurementbytes_generator, interval):
    measurements = []
    currtimestamp = None

    for measurementbytes in measurementbytes_generator:
        measurement = decode_measurement(measurementbytes)
        timestamp = measurement["timestamp"]

        if not currtimestamp:
            currtimestamp = timestamp

        if currtimestamp - timestamp < datetime.timedelta(seconds=interval):
            measurements.append(measurement)
            continue
        else:
            currtimestamp = timestamp
            yield measurements
            measurements = [measurement]


def groups_to_average(fieldname, measurement_generator):
    for measurements in measurement_generator:
        temperatures = [measurement[fieldname] for measurement in measurements]
        yield measurements[0]["timestamp"], round(util.avg(temperatures), 2)


if __name__ == "__main__":
    print(timeit.timeit('print(load_all_data_test())', number=1, globals=globals()))
