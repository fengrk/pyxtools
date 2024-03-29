# coding:utf-8
__author__ = 'rk.feng'

import asyncio
import gzip
import logging  # noqa
import os  # noqa
import random
import time
import typing
import unittest
from asyncio import futures
from collections import OrderedDict
from pprint import pprint
from urllib.parse import quote

import tornado.websocket
from tornado.websocket import WebSocketClientConnection, WebSocketClosedError

from pyxtools.basic_tools.md5_tools import create_guid, get_md5

REQUIRE_TEXT = """
pip install tornado>=5.1
"""


def build_device_id(route_key: str, device_hash: str = None) -> str:
    device_hash = device_hash or create_guid()
    return get_md5(route_key + "." + route_key[:-1])[:10] + get_md5(device_hash)[:5]


def check_device_id(route_key: str, device_id: str) -> bool:
    if len(route_key) < 3:
        return False
    if len(device_id) != 15:
        return False
    if get_md5(route_key + "." + route_key[:-1])[:10] != device_id[:10]:
        return False
    return True


class MessageBytesUtils:
    ws_id_byte_size = 2  # 16bit
    msg_no_size = 4  # 32bit
    frame_size = ws_id_byte_size + msg_no_size

    @classmethod
    def build_frame(cls, ws_id: int, msg_no: int) -> bytes:
        """ """
        return ws_id.to_bytes(MessageBytesUtils.ws_id_byte_size, byteorder='little', signed=False) + \
               msg_no.to_bytes(MessageBytesUtils.msg_no_size, byteorder='little', signed=False)

    @classmethod
    def parse_frame(cls, frame: bytes) -> typing.Tuple[int, int]:
        """ """
        return int.from_bytes(frame[:MessageBytesUtils.ws_id_byte_size], byteorder="little", signed=False), \
               int.from_bytes(frame[MessageBytesUtils.ws_id_byte_size:], byteorder="little", signed=False)

    @classmethod
    def build_message(cls, frame: bytes, msg: bytes) -> bytes:
        return frame[:MessageBytesUtils.frame_size] + msg

    @classmethod
    def parse_message(cls, message: bytes) -> typing.Tuple[bytes, bytes]:
        return message[:MessageBytesUtils.frame_size], message[MessageBytesUtils.frame_size:]

    @classmethod
    def compress_gzip(cls, msg_str: str) -> bytes:
        """ """
        return gzip.compress(msg_str.encode("utf-8"))

    @classmethod
    def decompress_gzip(cls, compressed_msg: bytes) -> str:
        """ """
        return gzip.decompress(compressed_msg).decode("utf-8")


class _RecvObj:
    __slots__ = ("fut", "waited")

    def __init__(self, fut: asyncio.Future, waited: float = 0, ):
        self.waited = waited  # waited的时间戳, <= 0 表示 还没被占用
        self.fut = fut

    @property
    def weight(self):
        had_data = bool(self.fut.cancelled() or self.fut.done())

        return 1 if had_data else 0, self.waited if self.waited > 0 else 0


class WsP2PServerHandler(tornado.websocket.WebSocketHandler):
    clients: typing.Dict[str, typing.List['WsP2PServerHandler']] = {}  # 记录节点注册 websocket. {route_key: [ws]}
    clients_counter: typing.Dict[str, int] = {}  # 记录节点注册 websocket. {route_key: counter}

    # base var
    route_key: str = None
    device_id: str = None
    ws_id: int = None

    def __init__(self, *args, **kwargs):
        super(WsP2PServerHandler, self).__init__(*args, **kwargs)
        self.log: logging.Logger = logging.getLogger(self.__class__.__name__)

    def check_origin(self, origin):
        """ 校验权限 """
        self.log.info(f"[check_origin][origin {origin}]")
        return True

    def _get_all_arguments(self, ) -> typing.Dict[str, str]:
        """ """
        headers = self.request.headers or {}
        args = self.request.arguments
        params = {}
        for a in args:
            params[a.lower()] = self.get_argument(a)
        for k, v in headers.items():
            params[k.lower()] = v

        return params

    async def open(self):
        """ 开启连接 """
        kwargs = self._get_all_arguments()
        self.route_key = kwargs.get('route_key', None)
        self.device_id = kwargs.get('device_id', None)
        if not self.route_key or not self.device_id:
            self.close()
            return

        if not check_device_id(route_key=self.route_key, device_id=self.device_id):
            self.close()
            return

        if self.route_key not in WsP2PServerHandler.clients:
            WsP2PServerHandler.clients[self.route_key] = []
            WsP2PServerHandler.clients_counter[self.route_key] = 0
        WsP2PServerHandler.clients[self.route_key].append(self)
        WsP2PServerHandler.clients_counter[self.route_key] += 1

        self.ws_id = WsP2PServerHandler.clients_counter[self.route_key]
        self.log.info(f"[OptWebsocket opened][route_key {self.route_key}, device_id {self.device_id}, "
                      f"ws_id {self.ws_id}]"
                      f"client device_id list {[x.device_id for x in WsP2PServerHandler.clients[self.route_key]]}")

        # tell client: ws_id
        asyncio.ensure_future(self.write_message(
            message=MessageBytesUtils.build_message(
                frame=MessageBytesUtils.build_frame(ws_id=0, msg_no=0),
                msg=self.ws_id.to_bytes(MessageBytesUtils.ws_id_byte_size, byteorder='little', signed=False),
            ),
            binary=True
        ))

    def on_message(self, message: bytes):
        """连接通信"""

        async def _send_msg(_ws: 'WsP2PServerHandler', _msg, _binary):
            # self.log.info(f"msg transfer to device_id {_ws.device_id}, msg {_msg}")
            try:
                await _ws.write_message(_msg, binary=_binary)
            except Exception as e:
                self.log.error(f"[on_message][device_id {_ws.device_id}, ws_id {_ws.ws_id}]"
                               f"ws write_message error {e}")

        binary = isinstance(message, bytes)
        if not binary:
            self.log.info(f"[on_message][route_key {self.route_key}, device_id {self.device_id},"
                          f" ws_id {self.ws_id}]msg {message}")
        else:
            self.log.info(f"[on_message][route_key {self.route_key}, device_id {self.device_id},"
                          f" ws_id {self.ws_id}]msg_size {len(message)}")

        ws_list = WsP2PServerHandler.clients.get(self.route_key, []) or []
        for ws in ws_list:
            # self.log.info(f"[ws_list]device_id {ws.device_id}, ws_id {ws.ws_id}")
            if ws.ws_id != self.ws_id:
                asyncio.ensure_future(_send_msg(ws, message, binary))

    def on_close(self):
        """关闭连接"""

        async def on_close_async():
            try:
                self.close()
            except Exception as e:
                self.log.exception('[close_ws]')

            if self.route_key and self.route_key in WsP2PServerHandler.clients:
                try:
                    _remove_index = None
                    for i, ws in enumerate(WsP2PServerHandler.clients[self.route_key]):
                        if ws.ws_id == self.ws_id:
                            _remove_index = i
                            break
                    if _remove_index is not None:
                        WsP2PServerHandler.clients[self.route_key].pop(_remove_index)
                except Exception as e:
                    self.log.error('[on_close][device_id :{}]'.format(self.device_id), exc_info=True)

        self.log.info(f"[close][route_key {self.route_key}, device_id {self.device_id}, "
                      f"ws_id {self.ws_id}][OptWebsocket closed]")

        asyncio.ensure_future(on_close_async())

    def on_ping(self, data):
        """
        实时更新操作台设备过期时间
        实时查询消息库，发送通知消息
        @param data:
        @return:
        """
        self.log.debug(f"[ping][route_key {self.route_key}, device_id {self.device_id}, "
                       f"ws_id {self.ws_id}]")


class WsP2PClient:
    def __init__(self, route_key: str, ws_url: str, logger: logging.Logger, device_hash: str = None):
        self.logger = logger

        self._ws_server_conn: WebSocketClientConnection = None
        self.device_id: str = build_device_id(route_key, device_hash)
        self.route_key: str = route_key
        self._send_cache: typing.OrderedDict[bytes, asyncio.Future] = OrderedDict()
        self._recv_cache: typing.List[_RecvObj] = []
        self.ws_url = ws_url + f"?device_id={quote(self.device_id)}&route_key={quote(self.route_key)}"
        self.ws_id: int = None
        self.msg_no: int = 0

        self._lock = asyncio.Lock()

    def _create_frame_id(self, ) -> bytes:
        try:
            return MessageBytesUtils.build_frame(ws_id=self.ws_id, msg_no=self.msg_no)
        finally:
            self.msg_no += 1

    async def _open(self):
        """ """
        if self._ws_server_conn is not None:
            return

        async with self._lock:
            if self._ws_server_conn is not None:
                return

            self.logger.info(f"route_key : {self.route_key}, device_id {self.device_id}")
            self._ws_server_conn = await tornado.websocket.websocket_connect(
                self.ws_url,
                connect_timeout=60,
                ping_interval=10,
                on_message_callback=self._on_message_callback,
            )

            # check self.ws_id
            for _ in range(10):
                if self.ws_id is None:
                    await asyncio.sleep(1)
            if self.ws_id is None:
                raise ValueError("self.ws_id cannot be null!")

    def _on_message_callback(self, message: bytes):
        async def on_message_async(msg: bytes):
            # self.logger.info(f"on_message {message}")
            frame_id, msg = MessageBytesUtils.parse_message(message=msg)
            if self.ws_id is None:
                ws_id, msg_no = MessageBytesUtils.parse_frame(frame=frame_id)
                if ws_id == 0 and msg_no == 0:
                    self.ws_id = int.from_bytes(msg, byteorder="little", signed=False)
                    self.logger.info(f"[_on_message_callback][ws_id {self.ws_id}]ws_id set!")
                return

            if frame_id in self._send_cache:
                # response
                if not self._send_cache[frame_id].cancelled() and not self._send_cache[frame_id].done():
                    self._send_cache[frame_id].set_result(msg)
            else:
                # request
                fut: asyncio.Future = None
                recv_obj_list = sorted(
                    [recv_obj for recv_obj in self._recv_cache if not recv_obj.fut.done() or not recv_obj.fut.cancelled()],
                    key=lambda x: x.weight, reverse=True
                )
                if recv_obj_list:
                    recv_obj = recv_obj_list[0]
                    fut = recv_obj.fut
                else:
                    recv_obj = _RecvObj(fut=asyncio.Future())
                    fut = recv_obj.fut
                    self._recv_cache.append(recv_obj)

                if not fut.done() and not fut.cancelled():
                    fut.set_result((frame_id, msg))

        asyncio.ensure_future(on_message_async(message))

    async def send(self, msg: bytes, timeout: int = 0) -> bytes:
        await self._open()
        assert self.ws_id is not None
        frame_id = self._create_frame_id()
        self._send_cache[frame_id] = asyncio.Future()
        if self._ws_server_conn is None:
            raise ValueError("websocket closed!")

        try:
            bin_message = MessageBytesUtils.build_message(
                frame=frame_id,
                msg=msg,
            )
            await self._ws_server_conn.write_message(message=bin_message, binary=True)
        except WebSocketClosedError:
            self._ws_server_conn = None
            raise ValueError("websocket closed!")

        if timeout and timeout > 0:
            try:
                res = await asyncio.wait_for(self._send_cache[frame_id], timeout=timeout)
            except futures.TimeoutError as e:
                if not self._send_cache[frame_id].cancelled() or not self._send_cache[frame_id].done():
                    self._send_cache[frame_id].set_exception(e)
                raise
        else:
            res = await self._send_cache[frame_id]
            del self._send_cache[frame_id]

        return res

    async def receive(self, handle_msg: typing.Callable[[bytes, bytes], typing.Awaitable[bytes]]):
        await self._open()
        assert self.ws_id is not None

        # get req
        fut: asyncio.Future = None
        recv_obj_list = sorted(
            [recv_obj for recv_obj in self._recv_cache if recv_obj.waited <= 0], key=lambda x: x.weight, reverse=True
        )
        if recv_obj_list:
            recv_obj = recv_obj_list[0]
            recv_obj.waited = time.time()
            fut = recv_obj.fut
        else:
            recv_obj = _RecvObj(fut=asyncio.Future(), waited=time.time())
            self._recv_cache.append(recv_obj)
            fut = recv_obj.fut

        frame_id, msg = await fut
        _remove_index = None
        for recv_i, recv_obj in enumerate(self._recv_cache):
            if id(recv_obj.fut) == id(fut):
                _remove_index = recv_i
                break
        if _remove_index is not None:
            self._recv_cache.pop(_remove_index)

        # handle req
        if handle_msg:
            resp = await handle_msg(frame_id, msg)
        else:
            resp = b""

        # send resp
        if self._ws_server_conn is None:
            raise ValueError("websocket closed!")

        try:
            bin_message = MessageBytesUtils.build_message(
                frame=frame_id,
                msg=resp,
            )
            await self._ws_server_conn.write_message(message=bin_message, binary=True)
        except WebSocketClosedError:
            self._ws_server_conn = None
            raise ValueError("websocket closed!")


class T(unittest.TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger()

        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger
        self.route_key = 'aaaxbbb2'
        self.ws_url = "wss://www.example.com/ws/p2p"

    def testServer(self):
        async def consume(frame_id: bytes, msg: bytes) -> bytes:
            await asyncio.sleep(random.randint(1, 3))
            msg_str = MessageBytesUtils.decompress_gzip(compressed_msg=msg)
            pprint(msg_str)
            return MessageBytesUtils.compress_gzip(msg_str=msg_str + " done!")

        async def s():
            x = WsP2PClient(route_key=self.route_key, ws_url=self.ws_url, logger=self.logger)
            while True:
                await x.receive(handle_msg=consume)

        asyncio.get_event_loop().run_until_complete(s())

    def testClient(self):
        async def send(c, msg: str, timeout=5) -> str:
            try:
                res_bytes = await c.send(MessageBytesUtils.compress_gzip(msg_str=msg), timeout=timeout)
                return MessageBytesUtils.decompress_gzip(res_bytes)
            except Exception as e:
                pass

            return ""

        async def c():
            x = WsP2PClient(route_key=self.route_key, ws_url=self.ws_url, logger=self.logger)
            i = 0
            while True:
                v_list = await asyncio.gather(*[
                    send(x, f"msg.{i + 1}"),
                    send(x, f"msg.{i + 2}"),
                ])
                for v in v_list:
                    pprint(v)
                i += 2

        asyncio.get_event_loop().run_until_complete(c())
