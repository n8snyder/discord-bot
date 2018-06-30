import discord, os

TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        em = discord.Embed(title='My Embed Title', description='My Embed Content.', colour=0xDEADBF)
        em.set_author(name='Someone', icon_url=client.user.default_avatar_url)
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, embed=em)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
