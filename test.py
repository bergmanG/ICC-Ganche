import sys
import numpy as np
import scipy.stats
import random
import edgeCache
import timer
from utils import sampleSplits, sampleFromSplits

'''
query_splits = splitSections(5,query.timestamps)

np.save('splits/query.npy',np.array(query_splits))

train_1_splits = translateSplits(5,train_1.timestamps, query_splits)

np.save('splits/train_1.npy',np.array(train_1_splits))

train_2_splits = translateSplits(5,train_2.timestamps, query_splits)

np.save('splits/train_2.npy',np.array(train_2_splits))
'''

original_query_numpy = np.load('splits/query.npy', allow_pickle=True)
train_1_numpy = np.load('splits/train_1.npy', allow_pickle=True)
train_2_numpy = np.load('splits/train_2.npy', allow_pickle=True)


original_merged_train_numpy = [train_1_numpy[i] + train_2_numpy[i]
                               for i in range(len(train_1_numpy))]

valid_indices = list(filter(lambda i: len(original_query_numpy[i]) > 0 and len(
    original_merged_train_numpy[i]) > 5, range(len(original_query_numpy))))

query_numpy = [original_query_numpy[i] for i in valid_indices]

merged_train_numpy = [original_merged_train_numpy[i] for i in valid_indices]


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h


splits_pool_size = int(sys.argv[2])
test_iterations = 5
cache_size = 8*splits_pool_size
query_size = 3*splits_pool_size

total_precision = []
total_recall = []
total_latency = []

threshold = float(sys.argv[1])

for i in range(test_iterations):
    total_cache_right = total_right = total_wrong = total_present = 0
    odd = random.choice([0, 1])  # select either odd or even splits
    merged_train_splits = merged_train_numpy[1::2]
    query_splits = query_numpy[1::2]
    sampled_splits_indices = sampleSplits(
        query_splits, int(splits_pool_size*float(sys.argv[3])))

    sampled_query_splits = [query_splits[i]
                            for i in sampled_splits_indices]

    sampled_train_splits = [merged_train_splits[i]
                            for i in sampled_splits_indices[:splits_pool_size]]

    train_ts = sampleFromSplits(
        sampled_train_splits, cache_size)

    splits_info = {'train_splits': original_merged_train_numpy, 'query_splits': original_query_numpy,
                   'sampled_query_splits': query_splits,
                   'train_splits_indices': sampled_splits_indices[:splits_pool_size]}
    my_cache = edgeCache.Cache(train_ts, threshold, splits_info)

    query_ts = sampleFromSplits(sampled_query_splits, query_size)

    for ts in query_ts:
        timer.start()
        r = my_cache.request(ts)
        timer.stop()
        if not r['expected miss']:
            total_present += 1
        if r['right']:
            total_right += 1
            if not r['miss']:
                total_cache_right += 1
        else:
            total_wrong += 1

    total_precision.append(total_right/query_size)
    total_recall.append(total_cache_right/total_present)
    total_latency.append(timer.reset()/query_size)


print('Threshold:', threshold, 'N Places:', splits_pool_size,
      'Precision:', mean_confidence_interval(total_precision),
      'Recall:', mean_confidence_interval(total_recall), 'Latency:',
      mean_confidence_interval(total_latency))
