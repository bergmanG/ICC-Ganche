import math
import dataset
import random


def degreesToRadians(degrees):
    return degrees * math.pi / 180


def distanceInMBetweenEarthCoordinates(lat1, lon1, lat2, lon2):
    # reference: https://stackoverflow.com/a/365853

    earthRadiusKm = 6371

    dLat = degreesToRadians(lat2-lat1)
    dLon = degreesToRadians(lon2-lon1)

    lat1 = degreesToRadians(lat1)
    lat2 = degreesToRadians(lat2)

    a = math.sin(dLat/2) * math.sin(dLat/2) +\
        math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return earthRadiusKm * c * 1000


def findCoord(timestamp):
    # return real coord of a timestamp
    # aproximates coord as an avarage of first GPS record before and after timestamp

    gps = dataset.getGPS(timestamp)

    latitude_before = gps.loc[gps['timestamp']
                              < timestamp, 'latitude'].iloc[-1]
    latitude_after = gps.loc[gps['timestamp'] > timestamp, 'latitude'].iloc[1]
    longitude_before = gps.loc[gps['timestamp']
                               < timestamp, 'longitude'].iloc[-1]
    longitude_after = gps.loc[gps['timestamp']
                              > timestamp, 'longitude'].iloc[1]
    return ((latitude_after + latitude_before)/2, (longitude_after + longitude_before)/2)


def splitSections(split_size, timestamps):
    # aproximates the route as a straight line, and divides it in splits of split_size meters

    splits = [[]]
    anchor = timestamps[5]
    anchor_coord = findCoord(anchor)
    # start at 5 to garantee every image timestamp is bigger than at least one gps record
    for t in range(5, len(timestamps)):
        t_coord = findCoord(timestamps[t])
        if distanceInMBetweenEarthCoordinates(*anchor_coord, *t_coord) <= split_size:
            splits[-1].append(timestamps[t])
        else:
            splits.append([timestamps[t]])
            anchor = timestamps[t]
            anchor_coord = findCoord(anchor)
    return splits


def sampleFromSplits(splits, k):
    # return k timestamps randomly selected
    # every split have equal probability of being sampled from
    samples = []
    splits_len = len(splits)

    ts_remaining = [len(s) for s in splits]
    split_order = []
    def can_still_sample(x): return ts_remaining[x] > 0
    for _ in range(k):
        r = random.choice(list(filter(can_still_sample, range(splits_len))))
        ts_remaining[r] -= 1
        split_order.append(r)

    for s in range(splits_len):
        to_sample = split_order.count(s)
        if to_sample > 0:
            samples.extend(random.sample(
                splits[s], k=min(len(splits[s]), to_sample)))
    return samples


def translateSplits(split_size, timestamps, ref_splits):
    r = []
    for s in ref_splits:
        if len(s) == 0:
            r.append([])
            continue
        ref_start_coord = findCoord(s[0])
        ref_end_coord = findCoord(s[-1])
        inside = []
        for ts in range(5, len(timestamps)):
            ts_coord = findCoord(timestamps[ts])
            if distanceInMBetweenEarthCoordinates(*ts_coord, *ref_start_coord) <= split_size and\
                    distanceInMBetweenEarthCoordinates(*ts_coord, *ref_end_coord) <= split_size:
                inside.append(timestamps[ts])
            elif len(inside) > 0:
                break
        r.append(inside)
    return r


def sampleSplits(splits, k):
    # return k random splits from all splits
    r = random.sample(list(range(len(splits))), k)
    r.sort()
    return r
