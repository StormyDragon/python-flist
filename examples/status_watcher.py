import logging
from flist import account_login, start_chat, opcode
from twisted.internet import reactor, defer

def log_status(data):
    logging.info(u"{character} is {status}: {statusmsg}".format(**data))

# Using the deferredGenerator instead of a callback chain which would look messier.
@defer.deferredGenerator
def connect(account, password, character_name):
    account = account_login(account, password)
    character = account.characters[character_name]
    d = start_chat(character, dev_chat=True)
    wfd = defer.waitForDeferred(d)
    yield wfd
    chat = wfd.getResult()
    logging.info("Attaching log_status method.")
    chat.protocol.add_op_callback(opcode.STATUS, log_status)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('flist').setLevel(logging.ERROR)  # Disregard messages that are not outright errors.
    from sys import argv
    connect(argv[1], argv[2], argv[3])
    reactor.run()
