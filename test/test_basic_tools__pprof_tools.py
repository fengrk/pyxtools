# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import time
import unittest

from pyxtools.basic_tools.pprof_tools import time_cost


class TestBasicToolsPprofTools(unittest.TestCase):

    def testSyncTimeCost(self):
        """ """

        @time_cost()
        def a():
            time.sleep(1)
            return 1

        @time_cost()
        def main():
            a_v = a()
            assert a_v == 1
            time.sleep(2)
            return 2

        self.assertEqual(main(), 2)

    def testAsyncTimeCost(self):
        """ """

        @time_cost()
        async def a():
            await asyncio.sleep(1)
            return 1

        @time_cost()
        async def main():
            a_v = await a()
            assert a_v == 1
            time.sleep(2)
            return 2

        v = asyncio.run(main())
        self.assertEqual(v, 2)
