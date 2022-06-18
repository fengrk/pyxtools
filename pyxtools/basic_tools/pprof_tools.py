# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import cProfile
import functools
import logging
import pstats
import re
import time
import typing


class TimeCostHelper(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._time_start = time.time()
        self._last_time = time.time()

    def dot(self, info_format: str = None):
        now = time.time()
        time_cost_seconds = now - self._last_time
        self._last_time = now
        if info_format:
            self.logger.info(info_format.format(time_cost_seconds))
        else:
            self.logger.info("Time cost {}s".format(time_cost_seconds))

    def sum(self, info_format: str = None):
        now = time.time()
        time_cost_seconds = now - self._time_start
        if info_format:
            self.logger.info(info_format.format(time_cost_seconds))
        else:
            self.logger.info("Total time cost {}s".format(time_cost_seconds))


def time_cost(min_s: float = None, handle_log: typing.Callable[[str], None] = print):
    """计算时间
    @time_cost(min_s=0.1, handle_log=print)
    def a():
        pass

    @time_cost(min_s=0.1, handle_log=print)
    async def b():
        pass
    """

    async def async_wrapper(func, args, kwargs, _handle_log, _min_s):
        time_start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            async_time_cost = time.time() - time_start
            if _min_s is None or async_time_cost >= _min_s:
                if _handle_log:
                    _handle_log(f"[time_cost][func {func.__name__}]time cost {async_time_cost:.3f}s")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time_start = time.time()
            if asyncio.iscoroutinefunction(func):
                return async_wrapper(func, args, kwargs, handle_log, min_s)
            else:
                try:
                    return func(*args, **kwargs)
                finally:
                    sync_time_cost = time.time() - time_start
                    if min_s is None or sync_time_cost >= min_s:
                        if handle_log:
                            handle_log(f"[time_cost][func {func.__name__}]time cost {sync_time_cost:.3f}s")

        return wrapper

    return decorator


def c_profile_demo():
    print(re)  # re must import
    cProfile.run('re.compile("foo|bar")')


def do_c_profile(prof_file: str):
    """
    ref: https://zhuanlan.zhihu.com/p/24495603
    Decorator for function profiling.

    @do_c_profile(prof_file="/tmp/abc.prof")
    def a():
        pass
    """

    def wrapper(func):
        def profiled_func(*args, **kwargs):
            # Flag for do profiling or not.
            profile = cProfile.Profile()
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            # Sort stat by internal time.
            sort_by = "tottime"
            ps = pstats.Stats(profile).sort_stats(sort_by)
            ps.dump_stats(prof_file)
            return result

        return profiled_func

    return wrapper


def parse_c_profile_file(prof_file: str):
    p = pstats.Stats(prof_file)
    p.strip_dirs().sort_stats("cumtime").print_stats(10, 1.0, ".*")


__all__ = ("time_cost", "do_c_profile", "parse_c_profile_file", "TimeCostHelper")
