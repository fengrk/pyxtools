# -*- coding:utf-8 -*-
from __future__ import absolute_import

import math
import re
import unittest

from pyxtools.basic_tools.cache_tools import LazyEnum, LazyProxy


class TestBasicToolsCacheTools(unittest.TestCase):

    def testRegexLazyEnum(self):
        """ """

        class ReZoo(LazyEnum):
            RE_NUM: LazyProxy[re.Pattern] = LazyProxy(re.compile, r'\d+')
            RE_LETTER: LazyProxy[re.Pattern] = LazyProxy(re.compile, r'[A-Za-z]+')

        re_num = ReZoo.RE_NUM
        self.assertTrue(isinstance(re_num.value, re.Pattern))
        self.assertEqual(id(re_num.value), id(ReZoo.RE_NUM.value))
        self.assertEqual(id(re_num.value), id(ReZoo.RE_NUM.value))

        self.assertEqual(ReZoo.RE_NUM.value.search('aAc123').group(), '123')
        self.assertEqual(ReZoo.RE_LETTER.value.search('aAc123').group(), 'aAc')

    def testPowerLazyEnum(self):
        """ """

        def my_pow(x):
            print('pow({})'.format(x))
            return math.pow(x, float(x))

        class ReZoo(LazyEnum):
            POW_ONE: LazyProxy[float] = LazyProxy(my_pow, 1)
            POW_TWO: LazyProxy[float] = LazyProxy(my_pow, 2)

        re_one = ReZoo.POW_ONE
        self.assertTrue(isinstance(re_one.value, float))
        self.assertEqual(id(re_one.value), id(ReZoo.POW_ONE.value))
        self.assertEqual(id(re_one.value), id(ReZoo.POW_ONE.value))

        self.assertEqual(ReZoo.POW_ONE.value, 1.0)
        self.assertEqual(ReZoo.POW_TWO.value, 4.0)
