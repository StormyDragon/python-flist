import sqlite3
import logging
from flist import account_login, start_chat, opcode
import asyncio
from functools import partial
from jinja2 import Template

logger = logging.getLogger('channel_manager')
logging.getLogger('').setLevel('DEBUG')
for name in ["FLN", "STA", "NLN"]:
    logging.getLogger("flist.fchat." + name).setLevel('WARN')
template = Template(open("template.j2").read())

"""
This bot can be invited to a channel to act as a topic moderator.
When it is given administrative powers, it will provide users with a method to update a topic according to the template.
In the case of this bot, users can tell it to add them or remove them from the topic.
"""

users_in_topics = {}


def topic_applicator(channel, character, message):
    global users_in_topics
    try:
        if message == "!add":
            users = users_in_topics.setdefault(channel.name, [])
            users.append(character)
            # Add the user to the topic.
            channel.set_description(template.render(
                channel=channel.title,
                channel_users=users,
                channel_operators=channel.operators
            ))
        elif message == "!remove":
            # Remove the user from the topic.
            users = users_in_topics.setdefault(channel.name, [])
            users.remove(character)
            channel.set_description(template.render(
                channel=channel.title,
                channel_users=users,
                channel_operators=channel.operators
            ))
        elif message == "!terminate":
            channel.set_description(channel.saved_topic)
            channel.send("I am leaving now, the example has concluded, I have restored the topic to it's previous glory.")
            channel.part()
    except ValueError:
        pass


async def chat_invite(chat, whom, channel_name):
    channel = await chat.join(channel_name)

    channel.send(
        "Hi there; I was invited by [user]{}[/user] to carry out this topic manager example\n"
        "When I am given op, I will take control of the channel topic\n"
        "/op {name} to proceed.\n"
        "/kick {name} to abort.".format(whom, name=character_name)
    )

    def make_op(message):
        chat.protocol.remove_op_callback(opcode.PROMOTE_OP, make_op)
        channel.saved_topic = channel.description
        channel.send(
            "Now that I am moderator of the channel, the following features are enabled\n"
            "    !add - Adds your icon to the channel topic.\n"
            "    !remove - Removes your icon from the channel topic.\n"
            "To conclude the example\n"
            "    !terminate - Restores the topic to the state it was in when I was opped."
        )
        channel.add_listener(topic_applicator)

    def channel_kick(message):
        chat.protocol.remove_op_callback(opcode.PROMOTE_OP, make_op)
        chat.protocol.remove_op_callback(opcode.KICK, channel_kick)

    chat.protocol.add_op_callback(opcode.PROMOTE_OP, make_op)
    chat.protocol.add_op_callback(opcode.KICK, channel_kick)


async def connect(account, password, character_name):
    account = await account_login(account, password)
    character = account.get_character(character_name)
    chat = await start_chat(character, dev_chat=False)
    development_channel = await chat.join("Development")

    def receive_invitation(message):
        development_channel.send("""[user]{sender}[/user] invited me to join [session="{title}"]{name}[/session] for some kinky one on one testing.""".format(**message))

        asyncio.ensure_future(chat_invite(chat, message["sender"], message["name"]))

    chat.protocol.add_op_callback(opcode.INVITE, receive_invitation)
    development_channel.send("python-flist example: Topic manager; Invite me to a channel to proceed.")
    logger.info("I am ready.")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    from sys import argv
    account = argv[1]
    character_name = argv[3]
    asyncio.ensure_future(connect(account, argv[2], character_name))
    asyncio.get_event_loop().run_forever()
