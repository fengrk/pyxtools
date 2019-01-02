# -*- coding:utf-8 -*-
import logging

import os

from .faiss_utils import FaissManager


class ImageIndexUtils(object):
    key_extend_list = "extend_list"

    def __init__(self, index_dir: str, dimension: int):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)
        self.db_index_dir = index_dir
        self.manager = FaissManager(
            index_path=os.path.join(index_dir, "faiss.index"),
            dimension=dimension
        )
        self.dimension = dimension
        self._key_distance = "distance"
        self._key_top_k = "top"

    def image_search(self, feature_list: list, top_k: int = 3, extend: bool = False) -> list:
        return [
            result for result in self.image_search_iterator(feature_list=feature_list, top_k=top_k, extend=extend)
        ]

    def image_search_iterator(self, feature_list: list, top_k: int = 3, extend: bool = False):
        distance_list, indices = self.manager.search(feature_list, top_k=top_k)

        for index in range(distance_list.shape[0]):
            image_result_list = []

            for i in range(top_k):
                image_index = indices[index][i]
                if image_index == self.manager.not_found_id:
                    break

                result_info = self.manager.index_info_list[image_index]
                info = {self._key_distance: distance_list[index][i], self._key_top_k: i}
                info.update(result_info)
                extend_image_index_list = info.pop(self.manager.key_extend_list) if \
                    result_info.get(self.manager.key_extend_list) else None

                # 扩展
                if extend and extend_image_index_list:
                    extend_list = []
                    for extend_image_id in extend_image_index_list:
                        tmp_info = info.copy()
                        tmp_info.update(self.manager.index_info_list[extend_image_id])
                        extend_list.append(tmp_info)

                    info[self.key_extend_list] = extend_list

                image_result_list.append(info)

            yield image_result_list

    def add_images(self, image_feature_list: list, image_info_list: list):
        assert len(image_feature_list) == len(image_info_list)
        self.manager.train(image_feature_list, info_list=image_info_list)


__all__ = ("ImageIndexUtils",)
