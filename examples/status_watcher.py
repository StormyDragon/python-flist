import logging
from flist import account_login, start_chat, opcode
import asyncio
from sys import argv

logger = logging.getLogger('status_watcher')
logging.getLogger('').setLevel('DEBUG')

async def log_status_async(status_provider):
    async for message in status_provider:
        logger.info("%(character)s is %(status)s: %(statusmsg)s", message)

async def connect(account, password, character_name):
    account = await account_login(account, password)
    character = account.get_character(character_name)
    chat = await start_chat(character)
    return chat

async def status_logger():
    logger.info("Starting chat.")
    chat = await connect(argv[1], argv[2], argv[3])
    logger.info("Attaching log_status method.")
    status_provider = chat.watch(opcode.STATUS)
    await log_status_async(status_provider)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)

    asyncio.get_event_loop().run_until_complete(status_logger())
