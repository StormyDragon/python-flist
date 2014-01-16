import logging
from flist import account_login, start_chat, opcode
import asyncio

logger = logging.getLogger('status_watcher')
def log_status(data):
    logger.info(u"{character} is {status}: {statusmsg}".format(**data))

@asyncio.coroutine
def connect(account, password, character_name):
    account = yield from account_login(account, password)
    character = account.get_character(character_name)
    logger.info("Starting chat.")
    chat = yield from start_chat(character, dev_chat=False)
    logger.info("Attaching log_status method.")
    chat.protocol.add_op_callback(opcode.STATUS, log_status)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    from sys import argv
    asyncio.async(connect(argv[1], argv[2], argv[3]))
    asyncio.get_event_loop().run_forever()
