import logging
from flist import account_login, start_chat, opcode
import asyncio

def log_status(data):
    logging.info(u"{character} is {status}: {statusmsg}".format(**data))

@asyncio.coroutine
def connect(account, password, character_name):
    account = yield from account_login(account, password)
    character = account.characters[character_name]
    logging.info("Starting chat.")
    chat = yield from start_chat(character, dev_chat=False)
    logging.info("Attaching log_status method.")
    chat.protocol.add_op_callback(opcode.STATUS, log_status)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('flist').setLevel(logging.ERROR)  # Disregard messages that are not outright errors.
    logging.getLogger('asyncio').setLevel(logging.ERROR)  # Disregard messages that are not outright errors.
    from sys import argv
    asyncio.Task(connect(argv[1], argv[2], argv[3]))
    asyncio.get_event_loop().run_forever()
