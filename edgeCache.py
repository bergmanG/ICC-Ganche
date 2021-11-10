import numpy as np
from netVLAD import multiple_encode, encode
import faiss
from utils import distanceInMBetweenEarthCoordinates, findCoord
import dataset
from edgeAPI import sendImg
import timer


class Cache:
    def __init__(self, train_ts, threshold, splits_info) -> None:
        self.splits_info = splits_info
        self.__threshold = threshold
        self.encode_dim = 16384
        self.knbrs = faiss.IndexFlatL2(self.encode_dim)
        self.__train_ts = train_ts
        self.train_encondings = multiple_encode(dataset.getDir, train_ts)
        self.knbrs.add(self.train_encondings)

    def __findSplit(self, ts, splits):
        # return which split a timestamp belongs to
        for i, s in enumerate(splits):
            if ts in s:
                return i
        raise SystemExit('error timestamp not found')

    def __runknn(self, query_ts, nn):
        self.query_encondings = encode(dataset.getDir, query_ts)
        timer.stop()
        for _ in range(2):
            self.knbrs.search(np.random.rand(
                1, self.encode_dim).astype(np.float32), nn)
        timer.start()
        _, nn_results = self.knbrs.search(self.query_encondings, nn)
        return nn_results

    def request(self, query_ts):
        result = {}
        knn = self.__runknn(query_ts, 10)[0]

        nn1_ts = self.__train_ts[knn[0]]
        nn1_split = self.__findSplit(nn1_ts, self.splits_info['train_splits'])
        nn1_encoding = self.train_encondings[knn[0]]
        nn2_encoding = None

        for n in knn:
            n_split = self.__findSplit(
                self.__train_ts[n], self.splits_info['train_splits'])
            if abs(n_split - nn1_split) > 1:
                nn2_encoding = self.train_encondings[n]
                break

        result['miss'] = True if self.__threshold == 0 else False

        if nn2_encoding is not None:
            nn1_vec_dist = np.linalg.norm(
                self.query_encondings[0]-nn1_encoding)
            nn2_vec_dist = np.linalg.norm(
                self.query_encondings[0]-nn2_encoding)

            if nn1_vec_dist >= self.__threshold*nn2_vec_dist:
                result['miss'] = True
                nn1_ts = sendImg(query_ts)

        timer.stop()
        q_split = self.__findSplit(
            query_ts, self.splits_info['sampled_query_splits'])
        result['expected miss'] = True if q_split not in self.splits_info['train_splits_indices'] else False

        result['right'] = True if distanceInMBetweenEarthCoordinates(
            *findCoord(query_ts), *findCoord(nn1_ts)) <= 5 else False
        timer.start()
        return result
