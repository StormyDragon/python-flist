import json
import logging
import flist.opcode as opcode
import asyncio
import aiohttp

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
        finally:
            logger.debug("Issuing on_close")
            self.on_close(0, "Websockets: Connection was closed.")

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
        def_func = lambda *args: None
        self.fchat_on_message = def_func
        self.fchat_on_open = def_func
        self.fchat_on_close = def_func

    def on_open(self):
        super().on_open()
        self.fchat_on_open()

    def on_close(self, code, reason):
        self.fchat_on_close(code, reason)

    def on_message(self, message):
        super().on_message(message)
        self.fchat_on_message(message)


class DefaultFChatTransport(FChatPinger, FChatTransport):
    pass


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

        for f in callbacks:
            f(j)

        for h in self.handlers:
            h(op, j)
        logger.getChild(op).info("<-- %s" % (message,))

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


class Character():
    def __init__(self, chat, name):
        """Characters are initiated as they become known."""
        self.name = str(name)
        self.websocket = chat.websocket

    def __unicode__(self):
        return self.name

    def account_ban(self):
        pass  # ACB { character: "character" }

    def make_op(self):
        pass  # AOP { character: "character" }

    def get_alts(self):
        pass  # AWC { character: "character" }

    def de_op(self):
        pass  # DOP { character: "character" }

    def ignore(self):
        pass  # IGN { action: "add", character: "character" }

    def notify_ignored(self):
        pass  # IGN { action: "notify", character: "character" }

    def unignore(self):
        pass  # IGN { action: "delete", character: "character" }

    def ip_ban(self):
        pass  # IPB { character: "character" }

    def kick(self):
        pass  # KIK { character: "character" }

    def kinks(self):
        pass  # KIN { character: "character" }

    def send(self, message):
        pass  # PRI { recipient: "recipient", message: "message" }

    def profile(self):
        pass  # PRO { character: "character" }

    def reward(self):
        pass  # RWD { character: "character" } (status crown (cookie))

    def report(self):
        pass  # SFC { action: "action", report: "report", character: "character" }

    def timeout(self, duration, message):
        pass  # TMO { character: "character",time: time, reason: "reason" } # Duration in minutes.

    def unban(self):
        pass  # UBN { character: "character" }

    def announce_typing(self, status):  # clear, paused, typing
        d = {'character': self.name, 'status': status}
        self.websocket.message(opcode.TYPING, d)


class Channel():
    def __init__(self, chat, channel, mode=None, title=None):
        """Channels are initiated as they become known."""
        self.protocol = chat.protocol
        self.name = channel
        self.mode = mode
        self.title = title or channel

        self.protocol.add_op_callback(opcode.CHANNEL_MESSAGE, self._channel_message)

        self.callbacks = []

    def add_listener(self, callback):
        """Add a listener; accepts f(character, message)"""
        self.callbacks.append(callback)

    def remove_listener(self, callback):
        self.callbacks.remove(callback)

    def _channel_message(self, message):
        if message['channel'] == self.name:
            for f in self.callbacks:
                message.pop('channel')
                f(self, **message)

    def banlist(self):
        pass  # CBL { channel: "channel" }

    def ban(self, character):
        pass  # CBU { channel: "channel", character: "character" }

    def set_description(self, newdescription):
        pass  # CDS { channel: "channel", description: "description" }

    def invite(self, character):
        pass  # CIU { channel: "channel", character: "character", title: "My very special channel" }

    def kick(self, character):
        pass  # CKU { channel: "channel", character: "character" }

    def make_op(self, character):
        pass  # COA { channel: "channel", character: "character" }

    def list_operators(self, character):
        pass  # COL { channel: "channel" }

    def remove_op(self, character):
        pass  # COR { channel: "channel", character: "character" }

    def unban(self, character):
        pass  # CUB { channel: "channel", character: "character" }

    def part(self):
        d = {'channel': self.name}
        self.protocol.message(opcode.LEAVE_CHANNEL, d)
        pass  # LCH { channel: "channel" }

    def join(self):
        d = {'channel': self.name}
        self.protocol.message(opcode.JOIN_CHANNEL, d)
        pass  # JCH { channel: "channel" }     JCH {"character": {"identity": "Hexxy"}, "channel": "Frontpage"}

    def send(self, message):
        d = {'channel': self.name, 'message': message}
        self.protocol.message(opcode.CHANNEL_MESSAGE, d)
        pass  # MSG { channel: "channel", message: "message" }
        # MSG {"message": "Right, evenin'", "character": "Aensland Morrigan", "channel": "Frontpage"}

    def advertise_channel(self):
        pass  # RAN { channel: "channel" }

    def roll(self, dice):
        pass  # RLL { channel: "channel", dice: "1d10" }

    def set_status(self, status):
        pass  # RST { channel: "channel", status: "status" } ("private", "public")


class Connection(object):
    def __init__(self, protocol, character):
        self.character = character
        self.public_channels = {}
        self.private_channels = {}
        self.characters = {}
        self.variables = {}

        self.protocol = protocol
        self.protocol.add_op_callback(opcode.LIST_OFFICAL_CHANNELS, self._update_public_channels)
        self.protocol.add_op_callback(opcode.LIST_PRIVATE_CHANNELS, self._update_private_channels)
        self.protocol.add_op_callback(opcode.VARIABLES, self._variables)

    def connect(self):
        deferrence = asyncio.Future()
        o = self.protocol.on_open

        def on_open():
            o()
            self._introduce()

        def on_connected(data):
            if data['identity'] == str(self.character):
                self.protocol.remove_op_callback(opcode.USER_CONNECTED, on_connected)
                deferrence.set_result(self)

        self.protocol.on_open = on_open
        self.protocol.add_op_callback(opcode.USER_CONNECTED, on_connected)
        self.protocol.connect()
        return deferrence

    def close(self):
        self.quit()

    def quit(self):
        self.protocol.close()
        del self.protocol
        del self.public_channels
        del self.private_channels
        del self.variables
        del self.characters
        del self.character

    def _variables(self, var):
        self.variables[var['variable']] = var['value']

    def _update_channels(self, update_list, channel_list):
        # {"channels":[{"name":"Dragons","mode":"both","characters":0},{"name":"Frontpage"
        #               ,"mode":"both","characters":0}, ... ]}
        # {"channels":[{"name":"ADH-********", "title": "Fuckit", "characters": 0}, ...]}
        channels = channel_list.get('channels', [])
        if channels:
            for chan in channels:
                if chan['name'] not in update_list:
                    chan.pop('characters')
                    c = Channel(self, **chan)
                    update_list[chan['name']] = c
        else:
            logger.error("Channel response without any channels.")

    def _introduce(self):
        data = {
            'method': 'ticket',
            'ticket': self.character.account.get_ticket(),
            'account': str(self.character.account),
            'character': str(self.character),
            'cname': "StormyDragons F-List Python client (stormweyr.dk)",
            'cversion': "pre-alpha",
        }
        self.protocol.message(opcode.IDENTIFY, data)

    def _update_public_channels(self, channel_list):
        self._update_channels(self.public_channels, channel_list)

    def _update_private_channels(self, channel_list):
        self._update_channels(self.private_channels, channel_list)

    def broadcast(self, message):
        self.protocol.message(opcode.BROADCAST, {'message': message})

    def create_channel(self, channelname):
        self.protocol.message(opcode.CREATE_PRIVATE_CHANNEL, {'channel': channelname})
        pass  # CCR { channel: "channel"

    def join(self, channelname):
        d = asyncio.Future()

        channel = self.public_channels.get(channelname, None)
        if channel:
            d.cancel()
            return

        def on_join(channel_data):
            if channel_data['channel'] == channelname:
                self.protocol.remove_op_callback(opcode.JOIN_CHANNEL, on_join)
                channel_data.pop('character')
                channel = Channel(self, **channel_data)
                self.public_channels[channelname] = channel
                d.set_result(channel)

        self.protocol.add_op_callback(opcode.JOIN_CHANNEL, on_join)
        self.protocol.message(opcode.JOIN_CHANNEL, {'channel': channelname})
        return d

    def update_global_channels(self):
        self.protocol.message(opcode.LIST_OFFICAL_CHANNELS)
        pass  # CHA

    def create_global_channel(self, channelname):
        self.protocol.message(opcode.CREATE_OFFICAL_CHANNEL, {'channel': channelname})
        pass  # CRC { channel: "channel" }

    def search_kinks(self, kink, genders):
        self.protocol.message(opcode.SEARCH, {'kink': kink, 'genders': list(genders)})
        pass
        # FKS { kink: "kinkid", genders: [array] }
        # FKS {"kink":"523","genders":["Male","Female","Transgender","Herm","Shemale","Male-Herm","Cunt-boy","None"]}

    def ignore_list(self):
        self.protocol.message(opcode.IGNORE, {'action': 'list'})
        pass  # IGN { action: "list" }

    def list_ops(self):
        self.protocol.message(opcode.LIST_GLOBAL_OPS)
        pass  # OPP

    def update_private_channels(self):
        self.protocol.message(opcode.LIST_PRIVATE_CHANNELS)
        pass  # ORS

    def status(self, status, message):
        packet = {
            'character': str(self.character),
            'status': str(status),
            'statusmsg': str(message)
        }
        # STA {"status": "looking", "statusmsg": "I'm always available to RP :)", "character": "Hexxy"}
        self.protocol.message(opcode.STATUS,
                              packet)

    def uptime(self):
        self.protocol.message(opcode.UPTIME)
