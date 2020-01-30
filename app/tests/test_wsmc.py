import timeit
import unittest
from app import const
from app import weatherdata


def load_all_data_per_file():
    offset = 0
    while True:
        data = weatherdata.load_data_per_file(offset=offset)
        if len(data) < 1:
            break
        offset += 1
        del data


def load_all_data_per_chunk():
    data = [1]
    i = 0
    while len(data) != 0:
        del data
        data = weatherdata.load_data_per_chunk(weatherdata.MAX_CHUNKSIZE, offset=i)
        i += 1
    return i


class TestStringMethods(unittest.TestCase):

    def test_load_all_data_per_file(self):
        print("Test load all data per file:",
              timeit.timeit('print(load_all_data_per_file())', number=1, globals=globals()))

    def test_load_all_data_per_chunk(self):
        print("Test load all data per chunk:",
              timeit.timeit('print(load_all_data_per_chunk())', number=1, globals=globals()))

    def test_iterate_wsamc(self):
        offset = 0
        while True:
            data = weatherdata.load_data_per_file(
                const.MEASUREMENTS_DIR, offset, weatherdata.WSMC_EXTENSION)

            if len(data) == 0:
                break

            measurementbytes_generator = weatherdata.iterate_dataset_left(data)

            for measurement in weatherdata.decode_measurement(measurementbytes_generator):
                print(measurement)

            offset += 1

if __name__ == '__main__':
    unittest.main()
