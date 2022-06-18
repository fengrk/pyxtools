# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import os
import typing
import unittest

from pyxtools.basic_tools.pickle_cache_tools import self_lazy_load, pickle_cache_decorator


class TestBasicToolsPickleCacheTools(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_file = "test_pickle_cache_tools.dat"
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def tearDown(self) -> None:
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def testSyncSelfLazyLoad(self):
        """ """

        class A:
            def __init__(self):
                self.a = 1
                self.b_call_count = 0
                self.c_call_count = 0

            @property
            @self_lazy_load()
            def b(self):
                print("calculate b")
                self.b_call_count += 1
                return "b"

            @self_lazy_load()
            def c(self):
                print("calculate c")
                self.c_call_count += 1
                return "c"

        obj = A()
        self.assertEqual(obj.a, 1)

        self.assertEqual(obj.b, "b")
        self.assertEqual(obj.b, "b")
        self.assertEqual(obj.b_call_count, 1)

        self.assertEqual(obj.c(), "c")
        self.assertEqual(obj.c(), "c")
        self.assertEqual(obj.c_call_count, 1)

    def testAsyncSelfLazyLoad(self):
        """ """

        class A:
            def __init__(self):
                self.a = 1
                self.b_call_count = 0
                self.c_call_count = 0

            @property
            @self_lazy_load()
            async def b(self):
                print("calculate b")
                self.b_call_count += 1
                return "b"

            @self_lazy_load()
            async def c(self):
                print("calculate c")
                self.c_call_count += 1
                return "c"

        async def main(equal_func: typing.Callable[[typing.Any, typing.Any], None] = None):
            obj = A()
            equal_func(obj.a, 1)

            equal_func(await obj.b, "b")
            equal_func(await obj.b, "b")
            equal_func(obj.b_call_count, 1)

            equal_func(await obj.c(), "c")
            equal_func(await obj.c(), "c")
            equal_func(obj.c_call_count, 1)

        asyncio.run(main(self.assertEqual))

    def testSyncPickleCacheDecorator(self):
        """ """

        class A:
            def __init__(self):
                self.a_call_count = 0

            @pickle_cache_decorator(cache_file=self.cache_file)
            def a(self, ):
                print("calculate a")
                self.a_call_count += 1
                return "a"

        obj = A()
        self.assertEqual(obj.a(), "a")
        self.assertEqual(obj.a(), "a")
        self.assertEqual(obj.a_call_count, 1)

    def testAsyncPickleCacheDecorator(self):
        """ """

        class A:
            def __init__(self):
                self.a_call_count = 0

            @pickle_cache_decorator(cache_file=self.cache_file)
            async def a(self, ):
                print("calculate a")
                self.a_call_count += 1
                return "a"

        async def main(equal_func: typing.Callable[[typing.Any, typing.Any], None] = None):
            obj = A()
            equal_func(await obj.a(), "a")
            equal_func(await obj.a(), "a")
            equal_func(obj.a_call_count, 1)

        asyncio.run(main(self.assertEqual))
