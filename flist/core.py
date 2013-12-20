import weakref
import api
import fchat
import logging

logger = logging.getLogger("flist")

class AccountMissingException(Exception):
    pass

class FList_Character():
    def __init__(self, charactername, account):
        self.charname = charactername
        self._account = weakref.ref(account)

    @property
    def account(self):
        val = self._account()
        if not val:
            raise AccountMissingException("This character has no account associated to it.")
        return val

    def start_chat(self, **kwargs):
        return fchat.Connection(self, **kwargs)

    def __unicode__(self):
        return self.charname


class FList_Account():
    def __init__(self, accountname, password):
        self.characters = {}
        self.account = accountname
        self.refresh(password)

    def refresh(self, password):
        data = api.get_ticket(self.account, password)
        self.bookmarks = data['bookmarks']
        self.friends = data['friends']
        self.ticket = data['ticket']
        for charname in data['characters']:
            c = FList_Character(charname, self)
            self.characters.setdefault(charname, c) # Update the character.

    def get_ticket(self):
        return self.ticket

    def __unicode__(self):
        return self.account





















