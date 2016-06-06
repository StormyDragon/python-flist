import asyncio
import logging

import aiohttp

from flist.chat import opcode as opcode

logger = logging.getLogger(__name__)


class ConnectionCallbacks(object):
    def on_open(self):
        pass

    def on_close(self, code, reason):
        pass

    def on_message(self, message):
        pass


class WebsocketsClientAdapter(ConnectionCallbacks):
    def __init__(self, url, loop=None):
        super().__init__()
        self.url = url
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)

    def connect(self):
        asyncio.ensure_future(self._connect(), loop=self.loop)

    def close(self):
        asyncio.ensure_future(self.websocket.close(), loop=self.loop)

    async def _connect(self):
        try:
            self.websocket = await self.session.ws_connect(self.url)
            asyncio.ensure_future(self._inputhandler(), loop=self.loop)
            self.on_open()
        except:
            logger.exception("Websocket error")
            self.on_close(-1, "Websockets: Shit broke")

    async def _inputhandler(self):
        try:
            async for message in self.websocket:
                if message.tp == aiohttp.MsgType.text:
                    self.on_message(message.data)
                elif message.tp == aiohttp.MsgType.closed:
                    logger.warn("Websocket connection closed.")
                    self.on_close(0, "Websockets: Connection was closed.")
                    break
                elif message.tp == aiohttp.MsgType.error:
                    logger.error("Websocket error")
                    self.on_close(-1, "Websockets: Connection error")
                    break
        except:
            logger.exception("Websocket Exception was thrown")
            self.on_close(-2, "Websockets: Exception")

    def send_message(self, message):
        self.websocket.send_str(message)


class FChatPinger(WebsocketsClientAdapter):
    def __init__(self, url, loop=None):
        super().__init__(url, loop)
        self.pinger = None

    def ping(self):
        self.send_message(opcode.PING)
        self.pinger = self.loop.call_later(45, self.ping)

    def on_open(self):
        self.pinger = self.loop.call_later(45, self.ping)
        super().on_open()

    def on_close(self, code, reason):
        if self.pinger:
            self.pinger.cancel()
        super().on_close(code, reason)

    def on_message(self, message):
        if self.pinger:
            self.pinger.cancel()
        self.pinger = self.loop.call_later(45, self.ping)
        super().on_message(message)

    def send_message(self, message):
        if self.pinger:
            self.pinger.cancel()
        self.pinger = self.loop.call_later(45, self.ping)
        super().send_message(message)


class FChatTransport(ConnectionCallbacks):
    def __init__(self):
        super().__init__()
        self.fchat_on_message = self._empty
        self.fchat_on_open = self._empty
        self.fchat_on_close = self._empty

    @staticmethod
    def _empty(*args):
        pass

    @staticmethod
    def _empty(*args):
        pass

    def on_open(self):
        super().on_open()
        self.fchat_on_open()

    def on_close(self, code, reason):
        super().on_close(code, reason)
        self.fchat_on_close(code, reason)

    def on_message(self, message):
        super().on_message(message)
        self.fchat_on_message(message)


class DefaultFChatTransport(FChatPinger, FChatTransport):
    pass
