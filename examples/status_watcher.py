import logging
from flist import account_login, start_chat, opcode
from twisted.internet import reactor

def log_status(data):
    logging.debug("{character} is {status}: {statusmsg}".format(**data))

def connect(account, password, character_name):
    account = account_login(account, password)
    character = account.characters[character_name]
    chat = start_chat(character, dev_chat=True)
    chat.websocket.add_op_callback(opcode.STATUS, log_status)
    return chat

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('flist').setLevel(logging.ERROR)  # Disregard messages from flist module.
    from sys import argv
    connect(argv[1], argv[2], argv[3])
    reactor.run()
