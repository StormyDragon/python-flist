def account_login(account, password):
    """Log in to an f-list account."""
    from account import Account
    return Account(account, password)
