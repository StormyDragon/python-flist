
def account_login(account, password):
    """Log in to an f-list account.
    :param account: F-list account name.
    :param password: Password for the account.
    """
    from account import Account
    return Account(account, password)

def start_chat(character, server="chat.f-list.net", dev_chat=False):
    """Start an instance of fchat using the specified character.
    :param character: Character instance
    :param server: The server to which we connect.
    :param dev_chat: determines which chat we connect to.
    """
    from fchat import Connection
    port = 8722 if dev_chat else 9722
    return Connection(character, server=server, port=port)