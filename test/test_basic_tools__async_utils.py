# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import time
import unittest

from pyxtools.basic_tools.async_utils import run_on_executor, run_in_asyncio


class TestBasicTools(unittest.TestCase):

    @run_in_asyncio
    async def testRunOnExecutor(self):
        @run_on_executor()
        def f1():
            time.sleep(1)
            return "f1"

        @run_on_executor()
        def f2(a):
            time.sleep(1)
            return "f2"

        @run_on_executor()
        def f3(a, **kwargs):
            time.sleep(1)
            return "f3"

        res1 = await f1()
        res2_1 = await f2(10)
        res2_2 = await f2(a=10)

        res3_1 = await f3(a=10, b=20)
        res3_2 = await f3(10, b=20)

        self.assertEqual(res1, "f1")
        self.assertEqual(res2_1, "f2")
        self.assertEqual(res2_2, "f2")
        self.assertEqual(res3_1, "f3")
        self.assertEqual(res3_2, "f3")

    def testRunInAsyncio(self):
        """ """

        @run_in_asyncio
        async def x():
            print("start...")
            await asyncio.sleep(1)
            print("stop!")
            return "ok"

        v = x()
        self.assertEqual(v, "ok")
