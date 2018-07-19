import random
import asyncio
import aiohttp
import json
import os
import discord
import arrow
from discord import Game
from discord.ext.commands import Bot

from utils import (is_alert_channel, RSVPMessage, RECOGNIZED_EMOJIS)

BOT_PREFIX = ("!")
TOKEN = os.environ['BOT_TOKEN']

client = Bot(command_prefix=BOT_PREFIX)

rsvp_messages = {}


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)


@client.command(name='rsvp_setup', pass_context=True)
async def rsvp_setup(context):
    if context.message.channel not in rsvp_messages.keys() and context.message.author.server_permissions.administrator:
        rsvp_message = await client.say('*No RSVPs*')
        rsvp_messages[context.message.channel] = RSVPMessage(rsvp_message)
        await client.pin_message(rsvp_message)


@client.command(name='rsvp_destroy', pass_context=True)
async def rsvp_destroy(context):
    if not context.message.author.server_permissions.administrator:
        return
    try:
        rsvp_message = rsvp_messages.pop(context.message.channel)
    except KeyError:
        return
    else:
        for alert in rsvp_message.alerts:
            await client.clear_reactions(alert.message)
        await client.delete_message(rsvp_message.message)


@client.event
async def on_reaction_add(reaction, user):
    try:
        rsvp_message = rsvp_messages[reaction.message.channel]
    except KeyError:
        return

    if reaction.emoji in RECOGNIZED_EMOJIS and client.user != reaction.message.author:
        alert = rsvp_message.create_alert(reaction.message)
        alert.responses.post(reaction, user)
        rsvp_message.compose_content()
        await client.edit_message(rsvp_message.message, rsvp_message.content)


@client.event
async def on_reaction_remove(reaction, user):
    try:
        rsvp_message = rsvp_messages[reaction.message.channel]
    except KeyError:
        return

    if reaction.emoji in RECOGNIZED_EMOJIS and client.user != reaction.message.author:
        alert = rsvp_message.get_alert(reaction.message)
        if alert:
            alert.responses.delete(reaction, user)
            rsvp_message.update_alerts()
            rsvp_message.compose_content()
            await client.edit_message(rsvp_message.message, rsvp_message.content)


@client.event
async def on_message_edit(before, after):
    try:
        rsvp_message = rsvp_messages[before.channel]
    except KeyError:
        return

    if client.user != before.author:
        alert = rsvp_message.get_alert(before)
        if alert:
            alert.update_message(after)
            rsvp_message.compose_content()
            await client.edit_message(rsvp_message.message, rsvp_message.content)


@client.event
async def on_message_delete(message):
    try:
        rsvp_message = rsvp_messages[message.channel]
    except KeyError:
        return

    if client.user != message.author:
        rsvp_message.delete_alert(message)
        rsvp_message.compose_content()
        await client.edit_message(rsvp_message.message, rsvp_message.content)

# on_reaction_clear is the same as on_message_delete


@client.event
async def on_reaction_clear(message, reactions):
    try:
        rsvp_message = rsvp_messages[message.channel]
    except KeyError:
        return

    if client.user != message.author:
        rsvp_message.delete_alert(message)
        rsvp_message.compose_content()
        await client.edit_message(rsvp_message.message, rsvp_message.content)


async def remove_reactions():
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(60*30)
        now = arrow.utcnow()
        for rsvp_message in rsvp_messages.values():
            for alert in rsvp_message.alerts:
                if (now - arrow.get(alert.message.timestamp)).seconds > 60*60 + 60*45:
                    await client.clear_reactions(alert.message)
        print('Finished removing reactions.')


client.loop.create_task(remove_reactions())
client.run(TOKEN)
