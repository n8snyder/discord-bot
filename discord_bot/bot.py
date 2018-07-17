import random
import asyncio
import aiohttp
import json
import os
import discord
import arrow
from discord import Game
from discord.ext.commands import Bot

from utils import (is_alert_channel, ReservedMessage, RECOGNIZED_EMOJIS)

BOT_PREFIX = ("?", "!")
TOKEN = os.environ['BOT_TOKEN']

client = Bot(command_prefix=BOT_PREFIX)

reserved_messages = {}


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)
    all_alert_channels = [
        channel for channel in client.get_all_channels() if is_alert_channel(channel)]
    for channel in all_alert_channels:
        message = await client.send_message(channel, '*No RSVPs*')
        reserved_message = ReservedMessage(message)
        reserved_messages[channel] = reserved_message
        await client.pin_message(message)


@client.event
async def on_reaction_add(reaction, user):
    if is_alert_channel(reaction.message.channel) and reaction.emoji in RECOGNIZED_EMOJIS and client.user != reaction.message.author:
        reserved_message = reserved_messages[reaction.message.channel]
        alert = reserved_message.create_alert(reaction.message)
        alert.responses.post(reaction, user)
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)


@client.event
async def on_reaction_remove(reaction, user):
    if is_alert_channel(reaction.message.channel) and reaction.emoji in RECOGNIZED_EMOJIS and client.user != reaction.message.author:
        reserved_message = reserved_messages[reaction.message.channel]
        alert = reserved_message.get_alert(reaction.message)
        alert.responses.delete(reaction, user)
        reserved_message.update_alerts()
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)


@client.event
async def on_message_edit(before, after):
    if is_alert_channel(before.channel) and client.user != before.author:
        reserved_message = reserved_messages[before.channel]
        alert = reserved_message.get_alert(before)
        if alert:
            alert.update_message(after)
            reserved_message.compose_content()
            await client.edit_message(reserved_message.message, reserved_message.content)


@client.event
async def on_message_delete(message):
    if is_alert_channel(message.channel) and client.user != message.author:
        reserved_message = reserved_messages[message.channel]
        reserved_message.delete_alert(message)
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)

# on_reaction_clear is the same as on_message_delete


@client.event
async def on_reaction_clear(message, reactions):
    if is_alert_channel(message.channel) and client.user != message.author:
        reserved_message = reserved_messages[message.channel]
        reserved_message.delete_alert(message)
        reserved_message.compose_content()
        await client.edit_message(reserved_message.message, reserved_message.content)


async def remove_reactions():
    await client.wait_until_ready()
    while not client.is_closed:
        now = arrow.utcnow()
        for reserved_message in reserved_messages.values():
            for alert in reserved_message.alerts:
                if (now - arrow.get(alert.message.timestamp)).seconds > 60*60 + 60*45:
                    await client.clear_reactions(alert.message)
        print('Finished removing reactions.')
        await asyncio.sleep(60*30)


client.loop.create_task(remove_reactions())
client.run(TOKEN)
