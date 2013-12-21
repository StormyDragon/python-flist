import json
from functools import wraps
from urllib import urlencode
from urllib2 import Request, urlopen

import logging
logger = logging.getLogger(__name__)

def get_ticket(account, password):
    """You'll receive a ticket and a ton of other things that you probably won't need unless you're
    making an f-chat client. Tickets are valid for 24 hours from issue, and invalidate all previous
    tickets for the account when issued."""
    data = {
        'account': account,
        'password': password,
    }
    r = Request("http://www.f-list.net/json/getApiTicket.php", urlencode(data))
    val = urlopen(r)
    ppp = val.read()
    d = json.loads(ppp)
    return d

# API definitions
flist_api_url = "http://www.f-list.net/json/api/{function}.php"

def flist_api_decorator(func):
    api_variables = func.func_code.co_varnames
    api_name = func.__name__

    @wraps(func)
    def wrapper(**kwargs):
        logger.info("F-List API call: {method}{arguments}".format(method=api_name, kwargs))
        data = {}
        for argument in api_variables:
            data[argument] = kwargs.get(argument)
        r = Request(flist_api_url.format(function=api_name.replace('_', '-')), urlencode(data))
        val = urlopen(r)
        ppp = val.read()
        d = json.loads(ppp)
        return d

    return wrapper

# ======================================== Bookmarks
@flist_api_decorator
def bookmark_add(account, ticket, name):
    """Bookmark a profile. Takes one argument, "name"."""
    pass

@flist_api_decorator
def bookmark_list(account, ticket):
    """List all bookmarked profiles."""
    pass

@flist_api_decorator
def bookmark_remove(account, ticket, name):
    """Remove a profile bookmark. Takes one argument, "name"."""
    pass

# ======================================== Character Data
@flist_api_decorator
def character_customkinks(account, ticket, name):
    """Get a character's custom kinks. Requires one parameter, "name"."""
    pass

@flist_api_decorator
def character_get(name):
    """Get basic characer info. Does not require the account and ticket form fields.
    Requires one parameter, "name"."""
    pass

@flist_api_decorator
def character_images(account, ticket, name):
    """Get a list of all character image urls, and some extra info like the dimensions.
    Requires one parameter, "name"."""
    pass

@flist_api_decorator
def character_info(account, ticket, name):
    """Get a character's profile info fields. Requires one parameter, "name"."""
    pass

@flist_api_decorator
def character_kinks(account, ticket):
    """Get a character's kinks. Requires one parameter, "name"."""
    pass

@flist_api_decorator
def character_list(account, ticket):
    """Get a list of all the account's characters."""
    pass

# ======================================== Miscellaneous Data
@flist_api_decorator
def group_list(account, ticket):
    """Get the global list of all f-list groups."""
    pass

@flist_api_decorator
def ignore_list(account, ticket):
    """Get a list of all profiles your account has on chat-ignore."""
    pass

@flist_api_decorator
def info_list():
    """Get the global list of profile info fields, grouped. Dropdown options include a list of the options.
    Does not require the account and ticket form fields."""
    pass

@flist_api_decorator
def kink_list(account, ticket):
    """Get the global list of kinks, grouped. Does not require the account and ticket form fields."""
    pass

# ======================================== Friend list data, Friend requests
@flist_api_decorator
def friend_list(account, ticket):
    """List all friends, account-wide, in a "your-character (dest) => the character's friend (source)" format."""
    pass

@flist_api_decorator
def friend_remove(account, ticket):
    """Remove a profile from your friends. Takes two argument, "source_name" (your char)
    and "dest_name" (the character's friend you're removing)."""
    pass

@flist_api_decorator
def request_accept(account, ticket):
    """Accept an incoming friend request. Takes one argument, "request_id", which you
    can get with the request-list endpoint."""
    pass

@flist_api_decorator
def request_cancel(account, ticket):
    """Cancel an outgoing friend request. Takes one argument, "request_id", which you can
    get with the request-pending endpoint."""
    pass

@flist_api_decorator
def request_deny(account, ticket):
    """Deny a friend request. Takes one argument, "request_id", which you can get with the request-list endpoint."""
    pass

@flist_api_decorator
def request_list(account, ticket):
    """Get all incoming friend requests."""
    pass

@flist_api_decorator
def request_pending(account, ticket):
    """Get all outgoing friend requests."""
    pass

@flist_api_decorator
def request_send(account, ticket):
    """Send a friend request. source_name, dest_name."""
    pass

del flist_api_decorator, flist_api_url
