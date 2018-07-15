import random
import asyncio
import aiohttp
import json
import os
import discord
from discord import Game
from discord.ext.commands import Bot

from utils import (get_channel_message, get_original_content,
                   add_user_to_content, remove_user_from_content, is_alert_channel, ReservedMessage, RECOGNIZED_EMOJIS)

BOT_PREFIX = ("?", "!")
TOKEN = os.environ['BOT_TOKEN']
CHANNEL_NAME = os.environ['BOT_REPORT_CHANNEL_NAME']


client = Bot(command_prefix=BOT_PREFIX)


# Keys are message ids, values are messages
alerts = {}
reserved_messages = {}


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)
    all_alert_channels = [
        channel for channel in client.get_all_channels() if is_alert_channel(channel)]
    for channel in all_alert_channels:
        message = await client.send_message(channel, '*Reserved*')
        reserved_message = ReservedMessage(message)
        reserved_messages[channel] = reserved_message
        await client.pin_message(message)


@client.event
async def on_reaction_add(reaction, user):
    if is_alert_channel(reaction.message.channel) and reaction.emoji in RECOGNIZED_EMOJIS:
        reserved_message = reserved_messages[reaction.message.channel]
        alert = reserved_message.get_or_create_alert(reaction.message.content)
        alert.responses.post(reaction, user)
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)


@client.event
async def on_reaction_remove(reaction, user):
    if is_alert_channel(reaction.message.channel) and reaction.emoji in RECOGNIZED_EMOJIS:
        reserved_message = reserved_messages[reaction.message.channel]
        alert = reserved_message.get_alert(reaction.message.content)
        alert.responses.delete(reaction, user)
        reserved_message.update_alerts()
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
