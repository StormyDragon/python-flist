
def account_login(account, password):
    """Log in to an f-list account."""
    from account import Account
    return Account(account, password)

def start_chat(character, **kwargs):
    """Start an instance of fchat using the specified character."""
    from fchat import Connection
    server = kwargs.get("server", "chat.f-list.net")
    port = 8722 if kwargs.get("dev_chat", False) else 9722
    return Connection(character, server=server, port=port)