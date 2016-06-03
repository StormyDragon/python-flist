
def account_login(account, password):
    """Log in to an f-list account.
    :param account: F-list account name.
    :param password: Password for the account.
    """
    from flist.account import Account
    account = Account(account, password)
    return account.login()


def start_chat(character, server="chat.f-list.net", dev_chat=False, url="wss://chat.f-list.net:9799"):
    """Start an instance of fchat using the specified character.
    :param character: Character instance
    :param server: The server to which we connect.
    :param dev_chat: determines which chat we connect to.
    :param url: A url to completely replace the server/port behaviour
    :return deferred which fires with the chat instance once the connection has been established and introduction fired.
    """
    from flist.fchat import Connection, FChatProtocol, DefaultFChatTransport
    transport = DefaultFChatTransport(url)
    protocol = FChatProtocol(transport)
    chat = Connection(protocol, character).connect()
    return chat


def start_dev_chat(character):
    return start_chat(character, url="wss://chat.f-list.net:8722")
