# -*- coding:utf-8 -*-
from __future__ import absolute_import

import unittest

from ..pytools import iter_list_with_size


class TestBasicTools(unittest.TestCase):
    def test_iter_list_with_size(self):
        src_list = [i for i in range(100)]
        raw_src_list = list(src_list)

        dst_list = []
        for part_list in iter_list_with_size(src_list, 20):
            dst_list.extend(part_list)

        self.assertEqual(len(raw_src_list), len(dst_list))
        self.assertEqual(sum(raw_src_list), sum(dst_list))
        self.assertEqual(len(src_list), 0)
