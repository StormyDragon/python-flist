import logging
from flist import account_login, start_chat, opcode
import asyncio

logger = logging.getLogger('status_watcher')
logging.getLogger('').setLevel('DEBUG')

async def log_status_async(status_provider):
    async for message in status_provider:
        logger.info("%(character)s is %(status)s: %(statusmsg)s", message)

async def connect(account, password, character_name):
    account = await account_login(account, password)
    character = account.get_character(character_name)
    logger.info("Starting chat.")
    chat = await start_chat(character)
    logger.info("Attaching log_status method.")
    status_provider = chat.provider(opcode.STATUS)
    await log_status_async(status_provider)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    from sys import argv
    coroutine = connect(argv[1], argv[2], argv[3])
    asyncio.get_event_loop().run_until_complete(coroutine)
