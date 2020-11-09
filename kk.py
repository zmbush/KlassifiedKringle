# A secret santa assignment bot?
# I would like it to take data from a google sheet and then send parts of that
#  data to members of the discord server
# I don't want to know who got me and vice versa

import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import state

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

state_path = os.path.join(os.path.dirname(__file__), 'kk.state')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$kk ", intents=intents)

states = state.State(state_path)


@bot.listen()
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(
    help='reply with whatever message is provided.',
    aliases=['reply']
)
async def say(ctx, msg):
    await ctx.send(msg)


@bot.command(
    help='Starts secret santa assignments.'
)
async def begin(ctx, begin_type):
    state = states.get(ctx.guild.id)
    state.data['type'] = begin_type
    await ctx.send("Starting...")


@bot.command(
    help='Ends the assugnments.'
)
async def end(ctx):
    state = states.get(ctx.guild.id)
    await ctx.send("Ending: {0[type]}".format(state.data))
    state.data.clear()

bot.run(os.getenv('BOT_TOKEN'))
