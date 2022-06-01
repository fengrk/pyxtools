# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio
import concurrent
import functools
from concurrent.futures import ThreadPoolExecutor


def get_asyncio_running_loop() -> asyncio.AbstractEventLoop:
    # if sys.version_info < (3, 7):
    #     return asyncio.get_event_loop()

    # return asyncio.get_running_loop()
    return asyncio.get_event_loop()


def run_on_executor(executor: concurrent.futures.ThreadPoolExecutor = None):
    """
    @run_on_executor()
    def a():
        time.sleep(5)

    res = await a()
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs:
                _func, _args = functools.partial(func, **kwargs), args
            else:
                _func, _args = func, args
            async_future = get_asyncio_running_loop().run_in_executor(
                executor,
                _func,
                *_args,
            )
            return async_future

        return wrapper

    return decorator  # type: ignore


def run_in_asyncio(func):
    """asyncio run
    @run_in_asyncio
    async def a():
        await asyncio.sleep(1)
        return 1

    if __name__ == '__main__':
        a()
    """

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not hasattr(run_in_asyncio, "_count"):
            run_in_asyncio._count = 0
        else:
            run_in_asyncio._count += 1

        if run_in_asyncio._count == 0:
            loop = get_asyncio_running_loop()
            return loop.run_until_complete(func(*args, **kw))
        else:
            return func(*args, **kw)

    return wrapper
