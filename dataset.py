import os
import pandas as pd
import sys
import config


class Dataset:
    def __init__(self, ts_dirs, gps_dir) -> None:
        self.dirs = ts_dirs
        self.gps = pd.read_csv(gps_dir)
        self.timestamps = []
        self.__last_ts_dir = []
        for d in ts_dirs:
            self.timestamps.extend(self.getTimestamps(d))
            self.__last_ts_dir.append(self.timestamps[-1])
        self.first_ts = self.timestamps[0]
        self.last_ts = self.timestamps[-1]

    def getTimestamps(self, dir):
        # return timestamps in a dir as a list of int with a prefix

        files = os.listdir(dir)
        files.sort()
        return [int(f[:-4]) for f in files]

    def contains(self, timestamp):
        return True if timestamp >= self.first_ts and timestamp <= self.last_ts else False

    def getDir(self, timestamp):
        for i, d in enumerate(self.__last_ts_dir):
            if timestamp <= d:
                return self.dirs[i]
        raise SystemError("Unable to find directory for timestamp")


used_dirs = 4
GAN = int(os.environ['GAN'])
type_dir = 'fake' if GAN else 'real'

day_2014_12_09_13_21_02 = Dataset(
    [f'{config.ROOT_DIR}/robotcar/2014-12-09-13-21-02/0%i/mono_right/'
     % (i) for i in range(1, used_dirs + 1)],
    f'{config.ROOT_DIR}/robotcar/gps/2014-12-09-13-21-02/gps/gps.csv')

day_2014_12_12_10_45_15 = Dataset(
    [f'{config.ROOT_DIR}/robotcar/2014-12-12-10-45-15/0%i/mono_right/'
     % (i) for i in range(1, used_dirs + 1)],
    f'{config.ROOT_DIR}/robotcar/gps/2014-12-12-10-45-15/gps/gps.csv')

night_2014_12_16_18_44_24 = Dataset(
    [f'{config.ROOT_DIR}/robotcar/2014-12-16-18-44-24/0%i/%s/mono_right/'
     % (i, type_dir) for i in range(1, used_dirs + 1)],
    f'{config.ROOT_DIR}/robotcar/gps/2014-12-16-18-44-24/gps/gps.csv')

night_2014_12_10_18_10_50 = Dataset(
    [f'{config.ROOT_DIR}/robotcar/2014-12-10-18-10-50/0%i/%s/mono_right/'
     % (i, type_dir) for i in range(1, used_dirs + 1)],
    f'{config.ROOT_DIR}/robotcar/gps/2014-12-10-18-10-50/gps/gps.csv')

datasets = [day_2014_12_09_13_21_02, night_2014_12_16_18_44_24,
            night_2014_12_10_18_10_50, day_2014_12_12_10_45_15]

query = datasets[0]
train_1 = datasets[1]
train_2 = datasets[2]


def getDir(timestamp):
    # match directory for a timestamp

    for ds in datasets:
        if ds.contains(timestamp):
            return ds.getDir(timestamp)
    raise SystemError("Unable to find Directory")


def getGPS(timestamp):
    # match gps for a timestamp

    for ds in datasets:
        if ds.contains(timestamp):
            return ds.gps
    raise SystemError("Unable to find GPS")
