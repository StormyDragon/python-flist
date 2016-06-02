import logging
from flist import account_login, start_chat
import asyncio
import random
import re

logger = logging.getLogger('dice_bot')


def roll_and_replace_dice(match):
    d = match.groupdict()
    number = int(d['number'])
    faces = int(d['faces'])
    return str(random.randint(number, number*faces))


def parse(dice):
    dice = dice.strip().replace(" ", "")
    rolled = re.sub(r"(?P<number>\d+)(?:d|D)(?P<faces>\d+)", roll_and_replace_dice, dice)
    dice_sum = 0
    parsed_dice = []
    for number in re.findall(r"((?:\+|-)?\d+)", rolled):
        dice_sum += int(number)
        parsed_dice.append(number)

    return ''.join(parsed_dice), dice_sum


def command_listener(channel, character, message):
    if message.startswith("!roll "):
        dice = message[6:]
        parsed, result = parse(dice)
        if parsed:
            packet = {'character': character, 'dice': parsed, 'outcome': result}
            out = "{character} rolled {dice} yielding {outcome}".format(**packet)
            channel.send(out)
            logger.info(out)
        else:
            channel.send("{character}: Nothing was interpreted.".format(character=character))

async def connect(account, password, character_name):
    account = await account_login(account, password)
    character = account.get_character(character_name)
    chat = await start_chat(character, dev_chat=False)
    channel = await chat.join("Development")
    channel.add_listener(command_listener)
    channel.send("I am a dicebot; example: !roll 2d5 + 20")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    from sys import argv
    asyncio.ensure_future(connect(argv[1], argv[2], argv[3]))
    asyncio.get_event_loop().run_forever()
