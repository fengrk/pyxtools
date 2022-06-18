# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import functools
import gc
import os
import pickle
import shutil

PICKLE_MAX_BYTES = 2 ** 31 - 1


def load_cache(cache_file: str) -> object:
    if not os.path.exists(cache_file):
        return None
    bytes_in = bytearray(0)
    input_size = os.path.getsize(cache_file)
    gc.disable()
    try:
        gc.collect()
        with open(cache_file, 'rb') as f_in:
            for _ in range(0, input_size, PICKLE_MAX_BYTES):
                bytes_in += f_in.read(PICKLE_MAX_BYTES)
        return pickle.loads(bytes_in)
    except Exception:
        return None
    finally:
        gc.enable()


def dump_cache(obj, cache_file: str):
    gc.disable()
    try:
        gc.collect()
        bytes_out = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        with open(cache_file + ".tmp", 'wb') as f_out:
            for idx in range(0, len(bytes_out), PICKLE_MAX_BYTES):
                f_out.write(bytes_out[idx:idx + PICKLE_MAX_BYTES])
    finally:
        gc.enable()

    shutil.move(cache_file + ".tmp", cache_file)


def pickle_cache_decorator(cache_file: str):
    """
    @pickle_cache(cache_file="/tmp/abc.dat")
    def a():
        pass

    @pickle_cache(cache_file="/tmp/abc.dat")
    async def a():
        pass
    """

    async def async_wrapper(func, args, kwargs, _cache_file):
        if _cache_file and os.path.exists(_cache_file):
            res = await asyncio.get_running_loop().run_in_executor(
                None, load_cache, _cache_file
            )
            if res is not None:
                return res

        result = await func(*args, **kwargs)
        if cache_file:
            await asyncio.get_running_loop().run_in_executor(
                None, dump_cache, result, _cache_file
            )
        return result

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                return async_wrapper(func, args, kwargs, cache_file)
            else:
                if cache_file and os.path.exists(cache_file):
                    result = load_cache(cache_file)
                    if result is not None:
                        return result

                result = func(*args, **kwargs)
                if cache_file:
                    dump_cache(obj=result, cache_file=cache_file)
                return result

        return wrapper

    return decorator


def self_lazy_load(attr_key_format: str = "__{}__"):
    """
    @self_lazy_load()
    def a(self, ):
        pass

    @self_lazy_load()
    async def a(self, ):
        pass
    """

    async def async_wrapper(func, args, kwargs, self, attr_name):
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        res = await func(*args, **kwargs)
        setattr(self, attr_name, res)
        return res

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            _method_name = func.__name__
            _attr_name = attr_key_format.format(_method_name)

            if asyncio.iscoroutinefunction(func):
                return async_wrapper(func, args, kwargs, self, _attr_name)
            else:
                if hasattr(self, _attr_name):
                    return getattr(self, _attr_name)
                res = func(*args, **kwargs)
                setattr(self, _attr_name, res)
                return res

        return wrapper

    return decorator
