
def account_login(account, password):
    """Log in to an f-list account.
    :param account: F-list account name.
    :param password: Password for the account.
    """
    from flist.account import Account
    account = Account(account, password)
    return account.login()

def start_chat(character, server="chat.f-list.net", dev_chat=False, url=None):
    """Start an instance of fchat using the specified character.
    :param character: Character instance
    :param server: The server to which we connect.
    :param dev_chat: determines which chat we connect to.
    :return deferred which fires with the chat instance once the connection has been established and introduction fired.
    """
    from flist.fchat import Connection, FChatProtocol, DefaultFChatTransport
    port = 8722 if dev_chat else 9799
    transport = DefaultFChatTransport(url or "wss://{server}:{port}".format(server=server, port=port))
    protocol = FChatProtocol(transport)
    chat = Connection(protocol, character).connect()
    return chat