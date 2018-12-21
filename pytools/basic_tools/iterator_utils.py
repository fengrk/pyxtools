# -*- coding:utf-8 -*-
from __future__ import absolute_import


def iter_list_with_size(src_list: list, size: int):
    """
        src_list would be modified when running
    """
    n_part = len(src_list) // size + 1
    while n_part >= 0:
        n_part -= 1
        part_src_list = src_list[:size]
        if part_src_list:
            yield part_src_list
            del src_list[:size]
        else:
            break


__all__ = ("iter_list_with_size",)
