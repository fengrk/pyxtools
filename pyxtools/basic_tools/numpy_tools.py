# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import time

import numpy as np
from enum import Enum
from scipy import spatial

_np_zero = 1e-15


class NormType(Enum):
    """
    feature = np.random.random((3, 10))
    assert feature.shape == (3, 10)

    if norm_type == NormType.l2:
        normalized_feature = normalize(feature, norm='l2', axis=0)  # 对d(10)维分别l2正则化
        # normalized_feature = feature/np.linalg.norm(feature, ord=2, axis=0)
    elif norm_type == NormType.all:
        normalized_feature = feature / np.sqrt(np.sum(np.power(feature, 2)))
    else:
        normalized_feature = feature
    """
    none = 0
    l2 = 1
    all = 2

    def normalize(self, feature: np.ndarray) -> np.ndarray:

        if self.name == "all":
            logging.warning("using {} if norm == 0".format(_np_zero))
            return feature / (np.sqrt(np.sum(np.power(feature, 2))) + _np_zero)
        elif self.name == "l2":
            logging.warning("using {} if norm == 0".format(_np_zero))
            norm_feature = np.linalg.norm(feature, ord=2, axis=0)
            return feature / np.add(norm_feature, _np_zero, out=norm_feature, where=norm_feature == 0)
        elif self.name == "none":
            return feature
        else:
            raise ValueError("unknown NormType: {}".format(self.name))


def calc_distance_pairs(vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
    """
        # todo nan found in result
    Args:
        vec1: array, shape is [m, d]
        vec2: array, shape is [n, d]

    Returns:
        array: shape is [m, n]
    """
    assert vec1.shape[1] == vec2.shape[1]
    assert len(vec1.shape) == len(vec2.shape) == 2

    return np.sqrt(
        -2 * np.dot(vec1, vec2.T) +
        np.sum(np.square(vec2), axis=1) +
        np.transpose([np.sum(np.square(vec1), axis=1)])
    )


def calc_distance_pairs_by_scipy(vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
    """

    Args:
        vec1: array, shape is [m, d]
        vec2: array, shape is [n, d]

    Returns:
        array: shape is [m, n]
    """
    assert vec1.shape[1] == vec2.shape[1]
    assert len(vec1.shape) == len(vec2.shape) == 2

    return spatial.distance_matrix(vec1, vec2, p=2, threshold=1e12)


def test_benchmark_distance():
    m, n, d = 10000, 20000, 512
    a = np.random.random((m, d))
    b = np.random.random((n, d))

    # distance
    _time_start = time.time()
    dis = calc_distance_pairs(a, b)
    assert dis.shape == (m, n)
    print("time cost {}s".format(time.time() - _time_start))

    # scipy distance: oom
    _time_start = time.time()
    dis = calc_distance_pairs_by_scipy(a, b)  # oom
    assert dis.shape == (m, n)
    print("time cost {}s".format(time.time() - _time_start))


__all__ = ("NormType", "calc_distance_pairs", "calc_distance_pairs_by_scipy",)
