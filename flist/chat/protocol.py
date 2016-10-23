import asyncio
import json
import logging
from inspect import isawaitable

from flist.chat import opcode as opcode

logger = logging.getLogger(__name__)


class FChatProtocol(object):
    """Websocket protocol with included ping handler
    connect method: return deferred when the protocol is established.

    add_op_callback: accepts a method which receives a dict object corresponding to the decoded JSON data.
    remove_op_callback

    add_message_handler: accepts a method which receives the opcode and dict of the decoded JSON data.
    remove_message_handler
    """

    def __init__(self, transport, loop=None):
        self.on_close = lambda *args: None
        self.on_open = lambda *args: None

        self.callbacks = {}
        self.handlers = []
        self.transport = transport

        self.pinger = None
        self.loop = loop or asyncio.get_event_loop()

        self.add_op_callback(opcode.PING, self._ping_handler)

    def connect(self):
        self.transport.fchat_on_message = lambda *args: self.on_message(*args)
        self.transport.fchat_on_close = lambda *args: self.on_close(*args)
        self.transport.fchat_on_open = lambda *args: self.on_open(*args)
        self.transport.connect()

    def close(self):
        self.transport.close()

    def _ping_handler(self, message):
        self.message(opcode.PING)

    @staticmethod
    def _load_json(message):
        try:
            j = json.loads(message[4:])
        except ValueError:
            j = None
        return j

    def on_message(self, message):
        op = message[:3]
        callbacks = self.callbacks.get(op, [])
        j = self._load_json(message)

        for f in callbacks.copy():
            # noinspection PyBroadException
            try:
                r = f(j)
                if isawaitable(r):
                    asyncio.ensure_future(r, loop=self.loop)
            except BrokenPipeError:
                callbacks.remove(f)  # Caused by a closed provider.
            except Exception:
                callbacks.remove(f)
                logger.exception("While processing callbacks another exception"
                                 " occurred, callback function has been removed")

        for h in self.handlers:
            h(op, j)
        logger.getChild(op).info("<-- %s", message)

    def _write(self, message):
        if self.transport:
            logger.getChild(message[:3]).info("--> %s", message)
            self.transport.send_message(message)
        else:
            logger.error("Attempt to write message to Missing client.")

    def message(self, op, di=None):
        if di:
            self._write("%s %s" % (op, json.dumps(di)))
        else:
            self._write(op)

    def add_op_callback(self, op, callback):
        """Callbacks take the form of f(message)"""
        self.callbacks.setdefault(op, []).append(callback)

    def remove_op_callback(self, op, callback):
        self.callbacks.setdefault(op, []).remove(callback)

    def add_message_handler(self, handler):
        """A message handler takes the form of f(opcode, message)"""
        self.handlers.append(handler)

    def remove_message_handler(self, handler):
        self.handlers.remove(handler)

    def callback(self, status):
        def deco(func):
            self.add_op_callback(status, func)
            return func

        return deco
