# -*- coding:utf-8 -*-
from __future__ import absolute_import

import asyncio


async def get_response_content(url, session):
    async with session.get(url) as response:
        return await response.read()


async def bound_fetch(sem, url, session, callback):
    # Getter function with semaphore.
    async with sem:
        content = await get_response_content(url, session)
        callback(url, content)
        return


def _demo_callback_func(url, response_content, ):
    print(url)


def async_get(url_list, max_cpu=None, max_request_per_cpu=None, callback_func=None):
    from aiohttp import ClientSession

    async def run(_url_list, sem):
        tasks = []

        # Create client session that will ensure we dont open new connection
        # per each request.
        async with ClientSession() as session:
            for url in _url_list:
                task = asyncio.ensure_future(bound_fetch(sem, url, session, callback_func))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        run(
            url_list,
            sem=asyncio.Semaphore(max_request_per_cpu if max_request_per_cpu > len(url_list) else len(url_list))
        ))
    loop.run_until_complete(future)
