import weakref
import flist.api as api
import logging
import asyncio

logger = logging.getLogger(__name__)

class AccountMissingException(Exception):
    pass

class Character():
    def __init__(self, charactername, account):
        self.charname = charactername
        self._account = weakref.ref(account)

    @property
    def account(self):
        val = self._account()
        if not val:
            raise AccountMissingException("This character has no account associated to it.")
        return val

    def __str__(self):
        return self.charname


class Account():
    def __init__(self, accountname, password):
        self.characters = {}
        self.account = accountname
        self.password = password

    @asyncio.coroutine
    def login(self):
        yield from self.refresh(self.password)
        return self

    @asyncio.coroutine
    def refresh(self, password):
        data = yield from api.get_ticket(self.account, password)
        self.bookmarks = data['bookmarks']
        self.friends = data['friends']
        self.ticket = data['ticket']
        for charname in data['characters']:
            c = Character(charname, self)
            self.characters.setdefault(charname, c) # Update the character.

    def get_ticket(self):
        return self.ticket

    def __str__(self):
        return self.account
