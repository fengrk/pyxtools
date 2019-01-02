# -*- coding:utf-8 -*-
import logging
import pickle
import time
from threading import Lock

import faiss
import numpy as np
import os
from enum import Enum


class IndexType(Enum):
    accurate = 0
    fast = 1
    compress = 2
    auto = 3

    @property
    def to_train(self) -> bool:
        if self.name == "compress":
            return True
        return False

    @property
    def index_factory(self) -> str:
        if self.name == "accurate":
            return "Flat"
        elif self.name == "fast":
            return "IVFx,Flat"
        elif self.name == "compress":
            return "IVF100,PQ8"

        return "Flat"


class FaissStoreInfo(object):
    key_extend_list = "extend_list"
    key_class_id = "class_id"
    key_image_id = "index"

    def __init__(self):
        self.dict = {}

    def to_dict(self) -> dict:
        return self.dict

    @classmethod
    def from_dict(cls, index_info: dict = None):
        info = FaissStoreInfo()
        if index_info is None:
            index_info = {}
        info.dict = index_info
        return info

    def list_extend_image_id(self) -> list:
        return self.dict.get(self.key_extend_list, [])

    @classmethod
    def parse_extend_list(cls, all_index_info: dict) -> dict:
        class_id_vs_images = {}
        for image_id, index_info in all_index_info.items():
            class_id_vs_images.setdefault(index_info[cls.key_class_id], []).append(image_id)

        # add extend list
        for image_id, index_info in all_index_info.items():
            extend_list_set = set(class_id_vs_images.get(index_info[cls.key_class_id], []))
            if image_id in extend_list_set:
                extend_list_set.remove(image_id)
            index_info[cls.key_extend_list] = list(extend_list_set)
        return all_index_info


class FaissManager(object):
    """
    """
    not_found_id = -1

    def __init__(self, index_path: str, dimension: int,
                 index_type: IndexType = IndexType.accurate,
                 has_gpu: bool = False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.faiss_index_file = index_path
        self.has_gpu = has_gpu
        self.faiss_index = None
        self.index_type = index_type
        self.dimension = dimension
        self._lock = Lock()

        # index info
        self._pkl_file = self.faiss_index_file + ".pkl"
        if os.path.exists(self._pkl_file):
            with open(self._pkl_file, "rb") as f:
                self.index_info = pickle.load(f)
        else:
            self.index_info = {}

    @property
    def need_to_retrain(self) -> bool:
        if os.path.exists(self.faiss_index_file) and os.path.exists(self._pkl_file):
            return False

        if os.path.exists(self.faiss_index_file):
            os.remove(self.faiss_index_file)

        if os.path.exists(self._pkl_file):
            os.remove(self._pkl_file)

        return True

    def get_faiss_info_obj(self, indices: int) -> FaissStoreInfo:
        return FaissStoreInfo.from_dict(self.index_info.get(indices))

    def train(self, feature_list, index_info: dict):
        self.prepare_index()
        # extend_list
        self.index_info = FaissStoreInfo.parse_extend_list(index_info)

        feature = self.reshape_feature_list(feature_list)

        if self.index_type.to_train:
            self.logger.info("training index...")
            time_start = time.time()
            self.faiss_index.train(feature)  # nb * d
            self.logger.info("success to train index! Cost {} seconds!".format(time.time() - time_start))

        self.faiss_index.add(feature)
        self.save()

    def reshape_feature_list(self, feature_list) -> np.ndarray:
        """  """
        feature = feature_list
        if isinstance(feature_list, list):
            # feature_list shape: [(1, self.d), (1, self.d)]
            feature = np.vstack(feature_list).reshape((len(feature_list), self.dimension))
        return feature

    def search(self, feature_list, top_k=10) -> (np.ndarray, np.ndarray):
        self.prepare_index()
        feature_list = self.reshape_feature_list(feature_list)
        length = feature_list.shape[0]

        time_start = time.time()
        distance_list, indices = self.faiss_index.search(feature_list, top_k)
        self.logger.info("cost {}s to search {} feature".format(time.time() - time_start, length))

        distance_list = distance_list.reshape((length, top_k))
        indices = indices.reshape((length, top_k))

        return distance_list, indices

    def _restore(self):
        """

        :rtype: object
        """
        if not os.path.exists(self.faiss_index_file):
            raise Exception("{} not exists!".format(self.faiss_index_file))

        return faiss.read_index(self.faiss_index_file)

    def prepare_index(self):
        # index
        if self.faiss_index is not None:
            return

        if os.path.exists(self.faiss_index_file):
            self.faiss_index = self._restore()
            return

        # create index
        if self.index_type.index_factory:
            self.faiss_index = faiss.index_factory(self.dimension, self.index_type.index_factory)
            if self.has_gpu:
                res = faiss.StandardGpuResources()  # use a single GPU
                self.faiss_index = faiss.index_cpu_to_gpu(res, 0, self.faiss_index)

    def save(self, ):
        assert self.faiss_index is not None

        with self._lock:
            faiss.write_index(self.faiss_index, self.faiss_index_file)

            with open(self._pkl_file, "wb") as f:
                pickle.dump(self.index_info, f)


__all__ = ("faiss", "IndexType", "FaissStoreInfo", "FaissManager")
