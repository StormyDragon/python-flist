import json
from urllib import urlencode
from urllib2 import Request, urlopen

import logging

"""
    F-List API interface.
"""

def get_ticket(account, password):
    # Hrm.. getApiTicket returns a lot of information, rather than just a ticket.
    # Ticket.
    # Characters, including the default.
    # Bookmarks.
    # Friend connections.
    data = {}
    data['account'] = account
    data['password'] = password
    r = Request("http://www.f-list.net/json/getApiTicket.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def add_bookmark(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/bookmark-add.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def remove_bookmark(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/bookmark-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def list_bookmarks():
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/bookmark-remove.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

########################################

def get_custom_kinks(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-customkinks.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def get_character(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-get.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def get_character_images(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-images.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def get_character_info(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-info.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def get_character_kinks(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-kinks.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def get_character_list(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/character-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

########################################


def list_group():
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/group-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def list_ignore():
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/ignore-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def list_profile_fields(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/info-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def list_kinks(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/kink-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

#########################################

def list_friends():
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/friend-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def friend_remove(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/friend-remove.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_accept(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/request-accept.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_cancel(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("http://www.f-list.net/json/api/request-cancel.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_deny(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("https://www.f-list.net/json/api/request-deny.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_list(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("https://www.f-list.net/json/api/request-list.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_pending(name):
    data = {}
    data['account'] = account
    data['ticket'] = ticket
    r = Request("https://www.f-list.net/json/api/request-pending.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

def request_send(character, other_character):
    data = {}
    data['source_name'] = character
    data['dest_name'] = other_character
    r = Request("https://www.f-list.net/json/api/request-send.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d
