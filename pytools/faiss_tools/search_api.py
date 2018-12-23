# -*- coding:utf-8 -*-
import logging

import os

from .faiss_utils import FaissManager


class ImageIndexUtils(object):
    def __init__(self, index_dir: str, dimension: int, ):
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
        distance_list, indices = self.manager.search(feature_list, top_k=top_k)
        result_list = []
        for index in range(len(distance_list)):
            image_result_list = []
            for i, image_id in enumerate(indices[index]):
                result_info = self.manager.get_faiss_info_obj(image_id)
                info = {self._key_distance: distance_list[index][i], self._key_top_k: i}
                info.update(result_info.to_dict())
                image_result_list.append(info)

                # 扩展
                if extend and result_info.list_extend_image_id():
                    for extend_image_id in result_info.list_extend_image_id():
                        tmp_info = info.copy()
                        tmp_info.update(self.manager.get_faiss_info_obj(extend_image_id).to_dict())
                        image_result_list.append(tmp_info)

            result_list.append(image_result_list)

        return result_list

    def add_images(self, image_feature_list: list, image_info_list: list):
        assert len(image_feature_list) == len(image_info_list)
        index_info = {index: image_info for index, image_info in enumerate(image_info_list)}
        self.manager.train(image_feature_list, index_info=index_info)


__all__ = ("ImageIndexUtils",)
