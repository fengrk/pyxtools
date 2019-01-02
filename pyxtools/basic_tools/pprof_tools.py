# -*- coding:utf-8 -*-
from __future__ import absolute_import

import cProfile
import logging
import pstats
import time

import functools
import re


def time_cost(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info("<{}> cost time: {}s".format(func.__name__, time.time() - start_time))
        return result

    return wrapper


def c_profile_demo():
    print(re)  # re must import
    cProfile.run('re.compile("foo|bar")')


def do_c_profile(prof_file: str):
    """
    ref: https://zhuanlan.zhihu.com/p/24495603
    Decorator for function profiling.
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


__all__ = ("time_cost", "do_c_profile", "parse_c_profile_file")
