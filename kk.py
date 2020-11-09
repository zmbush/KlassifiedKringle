# A secret santa assignment bot?
# I would like it to take data from a google sheet and then send parts of that
#  data to members of the discord server
# I don't want to know who got me and vice versa

import discord
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$assign"):
        member = message.guild.get_member_named(os.getenv('TEST_USER'))
        await message.channel.send(member.mention)

client.run(os.getenv('BOT_TOKEN'), bot=True)
