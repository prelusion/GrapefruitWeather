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

    @unittest.skip
    def test_load_all_data_per_file(self):
        print("Test load all data per file:",
              timeit.timeit('print(load_all_data_per_file())', number=1, globals=globals()))

    @unittest.skip
    def test_load_all_data_per_chunk(self):
        print("Test load all data per chunk:",
              timeit.timeit('print(load_all_data_per_chunk())', number=1, globals=globals()))

    def test_iterate_wsamc(self):
        offset = 0
        extension = weatherdata.WSAMC_EXTENSION

        while True:
            print("offset", offset)
            data = weatherdata.load_data_per_file(const.MEASUREMENTS_DIR, offset, extension)

            if len(data) == 0:
                print("no data")
                break

            measurementbytes_generator = weatherdata.iterate_dataset_left(data, extension)

            for measurementbytes in measurementbytes_generator:
                measurement = weatherdata.decode_measurement(measurementbytes, extension)
                print(measurement)

            offset += 1


if __name__ == '__main__':
    unittest.main()
