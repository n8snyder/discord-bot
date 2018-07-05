import random
import asyncio
import aiohttp
import json, os
import discord
from discord import Game
from discord.ext.commands import Bot
from discord.utils import find

BOT_PREFIX = ("?", "!")
TOKEN = os.environ['BOT_TOKEN']
CHANNEL_NAME = os.environ['BOT_REPORT_CHANNEL_NAME']

client = Bot(command_prefix=BOT_PREFIX)

RECOGNIZED_EMOJIS = [b'1\xe2\x83\xa3', b'3\xe2\x83\xa3', b'4\xe2\x83\xa3', 
                    b'5\xe2\x83\xa3', b'6\xe2\x83\xa3', b'7\xe2\x83\xa3', b'8\xe2\x83\xa3', 
                    b'9\xe2\x83\xa3', b'\xf0\x9f\x94\x9f', b'\xe2\x9d\x93', b'\xe2\x9d\x94']


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    await client.say(random.choice(possible_responses) + ", " + context.message.author.mention)


def get_channel_message(client, channel, content):
    #  returns the first message with the given content in the given channel.
    existing_message = find(lambda m: m.content==content and m.channel==channel, client.messages)
    return existing_message


@client.command()
async def square(number):
    squared_value = int(number) * int(number)
    await client.say(str(number) + " squared is " + str(squared_value))


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)

@client.event
async def on_reaction_add(reaction, user):
    reacted_message = reaction.message
    reporting_channel = discord.utils.get(reacted_message.server.channels, name=CHANNEL_NAME)
    existing_message = get_channel_message(client, reporting_channel, reacted_message.content)
    if not existing_message and reaction.emoji.encode('utf-8') in RECOGNIZED_EMOJIS:
        await client.send_message(reporting_channel, reacted_message.content)


@client.event
async def on_reaction_remove(reaction, user):
    reacted_message = reaction.message
    print('on reaction remove')
    print(reacted_message.reactions)
    if not reacted_message.reactions:
        #  remove message from reporting channel
        reporting_channel = discord.utils.get(reacted_message.server.channels, name=CHANNEL_NAME)
        existing_message = get_channel_message(client, reporting_channel, reacted_message.content)
        if existing_message:
            await client.delete_message(existing_message)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)