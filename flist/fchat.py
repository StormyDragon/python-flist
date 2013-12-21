import json
import logging
from twisted.internet import reactor, task
from autobahn.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from socket import socket, AF_INET, SOCK_STREAM
from urllib2 import urlopen
from select import select

logger = logging.getLogger(__name__)

ACCOUNT_BAN = "ACB"
ACCOUNT_UNBAN = "UBN"
ACCOUNT_TIMEOUT = "TMO"
SERVER_KICK = "KIK"
LIST_CHATOPS = "ADL"
PROMOTE_CHATOP = "AOP"
DEMOTE_CHATOP = "DOP"
LIST_ALTS = "AWC"
BROADCAST = "BRO"
CHANNEL_DESCRIPTION_CHANGED = "CDS"
LIST_OFFICAL_CHANNELS = "CHA"
BANLIST = "CBL"
BAN = "CBU"
UNBAN = "CUB"
TIMEOUT = "CTU"
CREATE_PRIVATE_CHANNEL = "CCR"
CREATE_OFFICAL_CHANNEL = "CRC"
CHANGE_CHANNEL_DESCRIPTION = "CDS"
INVITE = "CIU"
KICK = "CKU"
PROMOTE_CHANOP = "COA"
LIST_CHANOPS = "COL"
NUMBER_OF_CONNECTED_USERS = "CON"
DEMOTE_CHANOP = "COR"
SET_CHANNEL_OWNER = "CSO"
DEMOTE_CHANOP = "DOP"
ERROR = "ERR"
SEARCH = "FKS"
GONE_OFFLINE = "FLN"
SERVER_HELLO = "HLO"
INITIAL_CHANNEL_DATA = "ICH"
IDENTIFY = "IDN"
JOIN_CHANNEL = "JCH"
KINKS_DATA = "KID"
KINKS = "KIN"
PROFILE = "PRO"
RELOAD_SERVER_CONFIG = "RLD"
LEAVE_CHANNEL = "LCH"
LIST_CHARACTERS = "LIS"
USER_CONNECTED = "NLN"
IGNORE = "IGN"
FRIENDS_LIST = "FRL"
LIST_PRIVATE_CHANNELS = "ORS"
PING = "PIN"
PROFILE_DATA = "PRD"
PRIVATE_MESSAGE = "PRI"
CHANNEL_MESSAGE = "MSG"
ROLEPLAY_AD = "LRP"
ROLL = "RLL"
SET_CHANNEL_MODE = "RMO"
SET_PRIVATE_CHANNEL_STATE = "RST"
REWARD = "RWD"
REPORT = "SFC"
REAL_TIME_BRIDGE = "RTB"
STATUS = "STA"
SYSTEM_MESSAGE = "SYS"
TYPING = "TPN"
UPTIME = "UPT"
VARIABLES = "VAR"

class Websocket(object):
    def __init__(self, server, port, account, character, ticket, **kwargs):
        self.account = unicode(account)
        self.character = unicode(character)
        self.ticket = unicode(ticket)

        self.caching = kwargs.get('caching', True)
        self.on_close = kwargs.get('connection_lost', lambda: None)
        self.on_open = kwargs.get('connection_open', lambda: None)

        self.callbacks = {}
        self.handlers = []
        self.client = None

        class WebsocketClient(WebSocketClientProtocol):
            def onOpen(cl_self):
                logger.debug("Ready to introduce ourselves.!")
                self.client = cl_self
                self._introduce()
                self.PIN = task.LoopingCall(lambda: cl_self.sendMessage(PING))
                self.PIN.start(45, False)
                self.on_open()

            def connectionLost(cl_self, reason):
                logger.debug("Connection closed with reason {reason}".format(reason=reason))
                self.client = None
                if self.PIN:
                    self.PIN.stop()
                self.on_close()
                WebSocketClientProtocol.connectionLost(cl_self, reason)

            def onMessage(cl_self, message, binary):
                if self.PIN:
                    self.PIN.stop()
                    self.PIN.start(45, False)
                self.on_message(cl_self, message)

        factory = WebSocketClientFactory("ws://{server}:{port}".format(server=server, port=port), debug=False)
        factory.protocol = WebsocketClient
        self.factory = factory

    def connect(self):
        if not self.client:
            logger.debug("Websocket connecting.")
            connectWS(self.factory)

    def on_message(self, client, message):
        if message == PING:
          client.sendMessage(PING) # Pings are trivial, we don't care.
          return

        callbacks = self.callbacks.get(message[:3], [])
        for f in callbacks:
            f(json.loads(message[4:]))

        for h in self.handlers:
            h(message[:3], message[4:])
        logger.debug("<-- %s" % (message,))

    def _introduce( self ):
        data = {}
        data['method'] = 'ticket'
        data['ticket'] = self.ticket
        data['account'] = self.account
        data['character'] = self.character
        data['cname'] = "StormyDragons F-List Python client (stormweyr.dk)"
        data['cversion'] = "pre-alpha"
        self.message(IDENTIFY, data)

    def read(self):
        outval = self.cache[:]
        self.cache = []
        return outval

    def write(self, message):
        if self.client:
            logger.debug("--> %s" % (message,))
            self.client.sendMessage(message)
        else:
            logger.debug("Attempt to write message to Missing client.")

    def message(self, op, di=None):
        if di:
            self.write("%s %s" % (op, json.dumps(di)))
        else:
            self.write(op)

    def add_op_callback(self, op, callback):
        cbs = self.callbacks.setdefault(op, [])
        cbs.append(callback)

    def remove_op_callback(self, op, callback):
        self.callbacks.setdefault(op, []).remove(callback)

    def add_message_handler(self, handler):
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
        self.name = unicode(name)
        self.websocket = chat.websocket

    def __unicode__(self):
        return name

    def account_ban(self):
        pass # ACB { character: "character" }

    def make_op(self):
        pass # AOP { character: "character" }

    def get_alts(self):
        pass # AWC { character: "character" }

    def de_op(self):
        pass # DOP { character: "character" }

    def ignore(self):
        pass # IGN { action: "add", character: "character" }

    def notify_ignored(self):
        pass # IGN { action: "notify", character: "character" }

    def unignore(self):
        pass # IGN { action: "delete", character: "character" }

    def ip_ban(self):
        pass # IPB { character: "character" }

    def kick(self):
        pass # KIK { character: "character" }

    def kinks(self):
        pass # KIN { character: "character" }

    def send(self, message):
        pass # PRI { recipient: "recipient", message: "message" }

    def profile(self):
        pass # PRO { character: "character" }

    def reward(self):
        pass # RWD { character: "character" } (status crown (cookie))

    def report(self):
        pass # SFC { action: "action", report: "report", character: "character" }

    def timeout(self, duration, message):
        pass # TMO { character: "character",time: time, reason: "reason" } # Duration in minutes.

    def unban(self):
        pass # UBN { character: "character" }

    def announce_typing(self, status): # clear, paused, typing
        d = {}
        d['character'] = self.name
        d['status'] = self.status
        self.websocket.message(TYPING, d)

class Channel():
    def __init__(self, chat, name, mode):
        """Channels are initiated as they become known."""
        self.websocket = chat.websocket
        self.name = name
        self.mode = mode

        self.websocket.add_op_callback(MESSAGE, self._channel_message)

    def _channel_message(self, message):
        if message['channel'] is self.name:
            logger.info("%s - %s: %s" % (message['channel'], message['character'], message['message']))

    def banlist(self):
        pass # CBL { channel: "channel" }

    def ban(self, character):
        pass # CBU { channel: "channel", character: "character" }

    def set_description(self, newdescription):
        pass # CDS { channel: "channel", description: "description" }

    def invite(self, character):
        pass # CIU { channel: "channel", character: "character", title: "My very special channel" }

    def kick(self, character):
        pass # CKU { channel: "channel", character: "character" }

    def make_op(self, character):
        pass # COA { channel: "channel", character: "character" }

    def list_operators(self, character):
        pass # COL { channel: "channel" }

    def remove_op(self, character):
        pass # COR { channel: "channel", character: "character" }

    def unban(self, character):
        pass # CUB { channel: "channel", character: "character" }

    def part(self):
        d = {'channel': self.name}
        self.websocket.message(LEAVE_CHANNEL, d)
        pass # LCH { channel: "channel" }

    def join(self):
        d = {'channel': self.name}
        self.websocket.message(JOIN_CHANNEL, d)
        pass # JCH { channel: "channel" }     JCH {"character": {"identity": "Hexxy"}, "channel": "Frontpage"}

    def send(self, message):
        d = {'channel': self.name, 'message': message}
        self.websocket.message(MESSAGE, d)
        pass # MSG { channel: "channel", message: "message" } MSG {"message": "Right, evenin'", "character": "Aensland Morrigan", "channel": "Frontpage"}

    def advertise_channel(self):
        pass # RAN { channel: "channel" }

    def roll(self, dice):
        pass # RLL { channel: "channel", dice: "1d10" }

    def set_status(self, status):
        pass # RST { channel: "channel", status: "status" } ("private", "public")

class Connection():
    def __init__(self, character, **kwargs):
        self.character = character
        server = kwargs.get("server", "chat.f-list.net")
        port = 8722 if kwargs.get("dev_chat", False) else 9722
        port = kwargs.get("port", port)

        self.channels = {}
        self.characters = {}
        self.variables = {}

        self.websocket = Websocket(server, port, character.account, character, character.account.get_ticket(), **kwargs)
        self.websocket.connect()

        self.websocket.add_op_callback(LIST_OFFICAL_CHANNELS, self._update_channels)
        self.websocket.add_op_callback(VARIABLES, self._variables)

    def quit(self):
        del self.websocket
        del self.channels
        del self.variables
        del self.characters
        del self.character

    def _variables(self, var):
        self.variables[var['variable']] = var['value']

    def _update_channels(self, channel_list):
        # {"channels":[{"name":"Dragons","mode":"both","characters":0},{"name":"Frontpage","mode":"both","characters":0}, ... }
        channels = channel_list.get('channels', [])
        if channels:
            for chan in channels:
                if chan['name'] not in self.channels:
                    c = Channel(self, chan['name'], chan['mode'])
                    self.channels[chan['name']] = c
        else:
            logger.error("Channel response without any channels.")

    def broadcast(self, message):
        self.websocket.message(BROADCAST, {'message':message})

    def create_channel(self, channelname):
        self.websocket.message(CREATE_PRIVATE_CHANNEL, {'channel':channelname})
        pass # CCR { channel: "channel"

    def update_global_channels(self):
        self.websocket.message(LIST_OFFICAL_CHANNELS)
        pass # CHA

    def create_global_channel(self, channelname):
        self.websocket.message(CREATE_OFFICAL_CHANNEL, {'channel':channelname})
        pass # CRC { channel: "channel" }

    def search_kinks(self, kink, genders):
        self.websocket.message(SEARCH, {'kink':kink, 'genders': list(genders)})
        pass # FKS { kink: "kinkid", genders: [array] }    FKS {"kink":"523","genders":["Male","Female","Transgender","Herm","Shemale","Male-Herm","Cunt-boy","None"]}

    def ignore_list(self):
        self.websocket.message(IGNORE, {'action':'list'})
        pass # IGN { action: "list" }

    def list_ops(self):
        self.websocket.message(LIST_CHATOPS)
        pass # OPP

    def update_private_channels(self):
        self.websocket.message(LIST_PRIVATE_CHANNELS)
        pass # ORS

    def online(self, message):
        d = {}
        d['character'] = unicode(self.character)
        d['status'] = "online"
        d['statusmsg'] = unicode(message)
        self.websocket.message(STATUS, d)
        pass # STA {"status": "looking", "statusmsg": "I'm always available to RP :)", "character": "Hexxy"}

    def looking(self, message):
        d = {}
        d['character'] = unicode(self.character)
        d['status'] = "looking"
        d['statusmsg'] = unicode(message)
        self.websocket.message(STATUS, d)
        pass # STA {"status": "looking", "statusmsg": "I'm always available to RP :)", "character": "Hexxy"}

    def busy(self, message):
        d = {}
        d['character'] = unicode(self.character)
        d['status'] = "busy"
        d['statusmsg'] = unicode(message)
        self.websocket.message(STATUS, d)
        pass # STA {"status": "looking", "statusmsg": "I'm always available to RP :)", "character": "Hexxy"}

    def dnd(self, message):
        d = {}
        d['character'] = unicode(self.character)
        d['status'] = "dnd"
        d['statusmsg'] = unicode(message)
        self.websocket.message(STATUS, d)
        pass # STA {"status": "looking", "statusmsg": "I'm always available to RP :)", "character": "Hexxy"}

    def uptime(self):
        self.websocket.message(UPTIME)
