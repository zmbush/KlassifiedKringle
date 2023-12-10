# A secret santa assignment bot?
# I would like it to take data from a google sheet and then send parts of that
#  data to members of the discord server
# I don't want to know who got me and vice versa

import discord
import os

from dotenv import find_dotenv, load_dotenv
from discord.ext import commands
import state
import urllib
import re
import csv
import io
import random

load_dotenv(find_dotenv())

state_path = os.path.join(os.path.dirname(__file__), "kk.state")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="$kk ", intents=intents)

states = state.State(state_path)


@bot.listen()
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(help="loads a google doc")
async def load(ctx, doc_url):
    async with ctx.typing():
        print("yo")
        author_dm = ctx.message.author.dm_channel
        if not author_dm:
            author_dm = await ctx.message.author.create_dm()
        await ctx.message.delete()

        parts = re.match("https://docs.google.com/spreadsheets/d/([^/]+).*", doc_url)
        if not parts:
            await author_dm.send("Unable to parse google sheets url")
            return
        file = urllib.request.urlopen(
            "https://docs.google.com/spreadsheets/d/{}/export?format=csv".format(
                parts.group(1)
            )
        )
        text = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        user_field = reader.fieldnames[2]
        errors = []
        participants = []
        for person in reader:
            member = ctx.guild.get_member_named(person[user_field].strip())
            if member:
                person["mention"] = member.mention
                person["id"] = member.id
                participants.append(person)
            else:
                errors.append(f"Unable to find member named: `{person[user_field]}`")

        if errors:
            errors_str = "\n".join(errors)
            await author_dm.send(f"*Errors*:\n{errors_str}")
        else:
            shuffle_times = random.randint(5, 10)
            for _ in range(shuffle_times):
                random.shuffle(participants)
            await author_dm.send(
                f"Loaded {len(participants)} participants, and shuffled them {shuffle_times} times"
            )
            state = states.get(ctx.guild.id)
            state.data["participants"] = participants
            print([participant[user_field] for participant in participants])


@bot.command(help="Sends secret santa assignemnts to the appropriate users.")
async def send_assignments(ctx):
    await ctx.message.delete()
    state = states.get(ctx.guild.id)
    author_dm = ctx.message.author.dm_channel
    if not author_dm:
        author_dm = await ctx.message.author.create_dm()
    for i, participant in enumerate(state.data["participants"]):
        member = ctx.guild.get_member(participant["id"])
        if not member:
            await author_dm.send(
                f"Unable to find user with id: {participant['id']}."
                " Maybe they left the server?"
            )
            continue
        if member == bot.user:
            continue
        dm = member.dm_channel
        if not dm:
            dm = await member.create_dm()
        assignment = state.data["participants"][
            (i + 1) % len(state.data["participants"])
        ]
        message = f"""Hello {participant['mention']}! You have been assigned {assignment['mention']} for Secret Santa!

When preparing your gift for {assignment['mention']} please keep in mind the following:"""

        for key, value in assignment.items():
            if key in [
                "id",
                "mention",
                "Timestamp",
                "Email Address",
                "Do you want to be a pinch hitter?",
            ]:
                continue
            if not value.strip():
                continue
            key = key.strip().strip(":")
            msg = "\n> ".join(value.split("\n"))
            caveat = f"**{key}**:\n> {msg}\n"
            if len(message) + len(caveat) + 1 > 2000:
                await dm.send(message)
                message = f"""Secret Santa info for {assignment['mention']} (continued)
{caveat}"""
            else:
                message += "\n" + caveat

        # print(message)
        await dm.send(message)


bot.run(os.getenv("BOT_TOKEN"))
