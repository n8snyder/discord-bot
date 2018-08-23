import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()
import random
import asyncio
import aiohttp
import json

import discord
import arrow
from discord import Game
from discord.ext.commands import Bot


from rsvp_bot.models import (
    EventBoard, Server, Channel, Message, Event, Attendee, User)
from utils import (RSVPMessage, RECOGNIZED_EMOJIS, parse_expiration)

BOT_PREFIX = ("!")
TOKEN = os.environ['BOT_TOKEN']

client = Bot(command_prefix=BOT_PREFIX)

rsvp_messages = {}


#
# Commands
#

@client.command(name='rsvp_setup', description='Initial setup for channel rsvp message.', pass_context=True)
async def rsvp_setup(context):
    if (context.message.channel not in rsvp_messages.keys() and
            context.message.author.server_permissions.administrator):
        rsvp_message = await client.say('*No RSVPs*')
        rsvp_messages[context.message.channel] = RSVPMessage(rsvp_message)
        await client.pin_message(rsvp_message)
        # Update backend
        server = Server.objects.get_or_create(
            name=context.message.server.name, discord_id=context.message.server.id)[0]
        channel = Channel.objects.get_or_create(
            name=context.message.channel.name, discord_id=context.message.channel.id)[0]
        timestamp = arrow.get(context.message.timestamp, 'UTC').datetime
        message = Message.objects.get_or_create(
            content=rsvp_message.content, timestamp=timestamp, discord_id=rsvp_message.id)[0]
        expiration = rsvp_messages[context.message.channel].expiration
        EventBoard.objects.get_or_create(
            server=server, channel=channel, message=message, expiration=expiration)


@client.command(name='rsvp_destroy', description='Removes rsvp message from channel.', pass_context=True)
async def rsvp_destroy(context):
    if not context.message.author.server_permissions.administrator:
        return
    try:
        rsvp_message = rsvp_messages.pop(context.message.channel)
    except KeyError:
        return
    else:
        await client.delete_message(rsvp_message.message)
        EventBoard.objects.get(server__discord_id=context.message.server.id,
                               channel__discord_id=context.message.channel.id).delete()


@client.command(name='expires', description='Sets the amount of time for rsvps to expire.', pass_context=True)
async def expires(context):
    if not context.message.author.server_permissions.administrator:
        return
    try:
        rsvp_message = rsvp_messages[context.message.channel]
    except KeyError:
        return

    expiration = parse_expiration(context.view.read_rest().strip())
    rsvp_message.set_expiration(expiration)
    event_board = EventBoard.objects.get(
        server__discord_id=context.message.server.id, channel__discord_id=context.message.channel.id)
    event_board.expiration = expiration
    event_board.save()
    await client.add_reaction(context.message, '✅')

#
# Events
#


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with rsvps"))
    print("Logged in as " + client.user.name)
    backed_up_boards = EventBoard.objects.all()
    all_channels = client.get_all_channels()
    print(len(backed_up_boards))
    for board in backed_up_boards:
        channel = discord.utils.get(all_channels, id=board.channel.discord_id)
        timestamp = arrow.get(board.message.timestamp).naive
        async for message in client.logs_from(channel, around=timestamp):
            if message.id == board.message.discord_id:
                break
        rsvp_messages[channel] = RSVPMessage(
            message, expiration=board.expiration)


@client.event
async def on_reaction_add(reaction, user):
    try:
        rsvp_message = rsvp_messages[reaction.message.channel]
    except KeyError:
        return

    if reaction.emoji in RECOGNIZED_EMOJIS and client.user != reaction.message.author:
        alert = rsvp_message.create_alert(reaction.message)
        if alert:
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


async def remove_alerts():
    await client.wait_until_ready()
    while not client.is_closed:
        await asyncio.sleep(1)

        if any([rsvp_message.alerts for rsvp_message in rsvp_messages.values()]):
            print('Removing expired alerts...')
            await asyncio.sleep(60 * 5)
            for rsvp_message in rsvp_messages.values():
                for alert in rsvp_message.alerts:
                    if alert.is_expired:
                        rsvp_message.delete_alert(alert.message)
                rsvp_message.compose_content()
                await client.edit_message(rsvp_message.message, rsvp_message.content)


client.loop.create_task(remove_alerts())
client.run(TOKEN)
