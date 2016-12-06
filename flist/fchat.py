import asyncio
import logging
from functools import partial

import flist.chat.opcode as opcode
from flist.aiter_provider import CountCloserProvider, CloserProvider

logger = logging.getLogger(__name__)


class Character:
    def __init__(self, chat, name):
        """Characters are initiated as they become known."""
        self.name = str(name)
        self.protocol = chat.protocol

    def __str__(self):
        return self.name

    def account_ban(self):
        self.protocol.message(opcode.ACCOUNT_BAN, {'character': self.name})
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
        self.protocol.message(
            opcode.PRIVATE_MESSAGE,
            {'recipient': self.name, 'message': message}
        )

    def profile(self):
        self.protocol.message(
            opcode.PROFILE,
            {'character': self.name}
        )
        pass  # PRO { character: "character" } -> PROFILE_DATA

    def reward(self):
        self.protocol.message(
            opcode.REWARD,
            {'character': self.name}
        )

    def report(self):
        pass  # SFC { action: "action", report: "report", character: "character" }

    def timeout(self, duration, message):
        pass  # TMO { character: "character",time: time, reason: "reason" } # Duration in minutes.

    def unban(self):
        pass  # UBN { character: "character" }

    def announce_typing(self, status):  # clear, paused, typing
        d = {'character': self.name, 'status': status}
        self.protocol.message(opcode.TYPING, d)


class Channel:
    def __init__(self, chat, channel, mode=None, title=None):
        """Channels are initiated as they become known."""
        self.protocol = chat.protocol
        self.name = channel
        self.mode = mode
        self.title = title or channel
        self.description = ""
        self.operators = []

        self.protocol.add_op_callback(opcode.CHANNEL_MESSAGE, self._channel_message)
        self.protocol.add_op_callback(opcode.LIST_OPS, self._channel_operators)
        self.protocol.add_op_callback(opcode.SET_CHANNEL_DESCRIPTION, self._channel_description)

        self.callbacks = []

    def add_listener(self, callback):
        """Add a listener; accepts f(character, message)"""
        self.callbacks.append(callback)

    def remove_listener(self, callback):
        self.callbacks.remove(callback)

    def _channel_operators(self, message):
        self.operators = message["oplist"]

    def _channel_description(self, message):
        if message['channel'] == self.name:
            self.description = message['description']

    def _channel_message(self, message):
        if message['channel'] == self.name:
            for f in self.callbacks:
                message.pop('channel')
                f(self, **message)

    def banlist(self):
        pass  # CBL { channel: "channel" }

    def ban(self, character):
        pass  # CBU { channel: "channel", character: "character" }

    def set_description(self, new_description):
        # CDS { channel: "channel", description: "description" }
        d = {'channel': self.name, 'description': new_description}
        self.protocol.message(opcode.SET_CHANNEL_DESCRIPTION, d)

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
        # JCH { channel: "channel" }     JCH {"character": {"identity": "Hexxy"}, "channel": "Frontpage"}
        d = {'channel': self.name}
        self.protocol.message(opcode.JOIN_CHANNEL, d)

    def send(self, message):
        # MSG { channel: "channel", message: "message" }
        # MSG {"message": "Right, evenin'", "character": "Aensland Morrigan", "channel": "Frontpage"}
        d = {'channel': self.name, 'message': message}
        self.protocol.message(opcode.CHANNEL_MESSAGE, d)

    def advertise_channel(self):
        pass  # RAN { channel: "channel" }

    def roll(self, dice):
        pass  # RLL { channel: "channel", dice: "1d10" }

    def set_status(self, status):
        pass  # RST { channel: "channel", status: "status" } ("private", "public")


class ItemEnricher:
    def __init__(self, callable):
        self.callable = callable

    def __call__(self, opcode, message):
        enriched_message = message.copy()
        self.callable(enriched_message)


class Connection(object):
    def __init__(self, protocol, character):
        self._closables = [protocol]
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
        c = self.protocol.on_close

        def on_open():
            o()
            self._introduce()
            self.protocol.on_close = c

        def on_connected(data):
            try:
                if data['identity'] == str(self.character):
                    deferrence.set_result(self)
                else:
                    logger.error(data)
                    deferrence.set_exception(Exception("Received invalid identity response."))
            finally:
                self.protocol.remove_op_callback(opcode.USER_CONNECTED, on_connected)

        def on_close(reason):
            c(reason)
            deferrence.set_exception(ConnectionResetError(reason))

        self.protocol.on_open = on_open
        self.protocol.add_op_callback(opcode.USER_CONNECTED, on_connected)
        self.protocol.connect()
        return deferrence

    def close(self):
        self.quit()

    def quit(self):
        for c in self._closables:
            c.close()
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
            'ticket': self.character.account.ticket,
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
        # CCR { channel: "channel"
        self.protocol.message(opcode.CREATE_PRIVATE_CHANNEL, {'channel': channelname})

    def join(self, channelname):
        d = asyncio.Future()

        channel = self.public_channels.get(channelname, None)
        if channel:
            d.set_result(channel)
            return d

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
        # CHA
        self.protocol.message(opcode.LIST_OFFICAL_CHANNELS)

    def create_global_channel(self, channelname):
        # CRC { channel: "channel" }
        self.protocol.message(opcode.CREATE_OFFICAL_CHANNEL, {'channel': channelname})

    def search_kinks(self, kink, genders):
        # FKS { kink: "kinkid", genders: [array] }
        # FKS {"kink":"523","genders":["Male","Female","Transgender","Herm","Shemale","Male-Herm","Cunt-boy","None"]}
        self.protocol.message(opcode.SEARCH, {'kink': kink, 'genders': list(genders)})

    def ignore_list(self):
        # IGN { action: "list" }
        self.protocol.message(opcode.IGNORE, {'action': 'list'})

    def list_ops(self):
        # OPP
        self.protocol.message(opcode.LIST_GLOBAL_OPS)

    def update_private_channels(self):
        # ORS
        self.protocol.message(opcode.LIST_PRIVATE_CHANNELS)

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

    def watch(self, opcode_, *, count=None):
        closer = partial(self.protocol.remove_op_callback, opcode_)
        if count:
            provider = CountCloserProvider(closer=closer, count=count)
        else:
            provider = CloserProvider(closer=closer)
        self.protocol.add_op_callback(opcode_, ItemEnricher(provider.put_item))
        self._closables.append(provider)
        return provider
