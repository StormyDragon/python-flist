import logging
from flist import account_login, start_chat
from twisted.internet import reactor, defer
import random
import re

def roll_and_replace_dice(match):
    d = match.groupdict()
    number = int(d['number'])
    faces = int(d['faces'])
    return unicode(random.randint(number, number*faces))

def parse(dice):
    dice = dice.strip().replace(" ", "")
    rolled = re.sub(ur"(?P<number>\d+)(?:d|D)(?P<faces>\d+)", roll_and_replace_dice, dice)
    sum = 0
    parsed_dice = []
    for number in re.findall(r"((?:\+|-)?\d+)", rolled):
        sum += int(number)
        parsed_dice.append(number)

    return ''.join(parsed_dice), sum

def command_listener(channel, character, message):
    if message.startswith("!roll "):
        dice = message[6:]
        parsed, result = parse(dice)
        if parsed:
            packet = {'character': character, 'dice': parsed, 'outcome': result}
            out = "{character} rolled {dice} yielding {outcome}".format(**packet)
            channel.send(out)
            logging.info(out)
        else:
            channel.send("{character}: Nothing was interpreted.".format(character=character))

@defer.deferredGenerator
def connect(account, password, character_name):
    account = account_login(account, password)
    character = account.characters[character_name]
    wfd = defer.waitForDeferred(start_chat(character, dev_chat=True))
    yield wfd
    chat = wfd.getResult()
    wfd = defer.waitForDeferred(chat.join("Development"))
    yield wfd
    channel = wfd.getResult()
    channel.add_listener(command_listener)
    channel.send("I am a dicebot; example: !roll 2d5 + 20")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.getLogger('flist').setLevel(logging.ERROR)  # Disregard debug messages from flist module.
    from sys import argv
    connect(argv[1], argv[2], argv[3])
    reactor.run()
