import logging
from twisted.internet import reactor
import flist

def log_status(data):
    logging.debug("{character} is {status}: {statusmsg}".format(**data))

def on_disconnect():
    reactor.callLater(60, connect)

def connect():
    account = flist.Account('account', 'password')
    char = account.characters['character']
    chat = char.start_chat(dev_chat=True)
    chat.websocket.add_op_callback(flist.fchat.STATUS, log_status)
    return chat

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    connect()
    reactor.run()
