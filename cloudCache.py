from netVLAD import multiple_encode, cloud_encode
import faiss
import dataset
import numpy as np
import random


class Cache:
    def __init__(self, train_ts):
        self.encode_dim = 16384*2
        self.knbrs = faiss.IndexFlatL2(self.encode_dim)
        self.__train_ts = train_ts
        self.train_encondings = multiple_encode(dataset.getDir, train_ts)
        self.knbrs.add(self.train_encondings)

    def __runknn(self, image, nn):
        self.query_encondings = cloud_encode(image)
        _, nn_results = self.knbrs.search(self.query_encondings, nn)
        return nn_results

    def request(self, image):
        knn = self.__runknn(image, 1)[0]

        nn1_ts = self.__train_ts[knn[0]]

        return nn1_ts


def homogeneus_sample(n, splits):
    samples = []
    splits_len = len(splits)

    for s in range(splits_len):
        samples.extend(random.sample(
            splits[s], k=min(len(splits[s]), n)))
    return samples


original_query_numpy = np.load('splits/query.npy', allow_pickle=True)
train_1_numpy = np.load('splits/train_1.npy', allow_pickle=True)
train_2_numpy = np.load('splits/train_2.npy', allow_pickle=True)


original_merged_train_numpy = [train_1_numpy[i] + train_2_numpy[i]
                               for i in range(len(train_1_numpy))]

valid_indices = list(filter(lambda i: len(original_query_numpy[i]) > 0 and len(
    original_merged_train_numpy[i]) > 5, range(len(original_query_numpy))))

original_query_numpy = [original_query_numpy[i] for i in valid_indices]
train_1_numpy = [train_1_numpy[i] for i in valid_indices]

original_query_numpy = original_query_numpy[1::2]
train_1_numpy = train_1_numpy[1::2]

day_ts = homogeneus_sample(5, original_query_numpy)
night_ts = homogeneus_sample(5, train_1_numpy)

cache = Cache(day_ts+night_ts)
