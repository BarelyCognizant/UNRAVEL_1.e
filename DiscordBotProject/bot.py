# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

import character_sheet_handler as csh

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@bot.command(name="test", help="test")
@commands.has_role("bot_tester")
async def test(ctx):
    await ctx.send("test")


@bot.command(name="createPlayer", help="Create an Player with a given name \n name: name")
@commands.has_role("gremlin")
async def add_new_player(ctx, name):
    await ctx.send(csh.add_new_player(name))


@bot.command(name="viewPlayer", help="View a given player's character sheet \n name: the name of the player to view")
async def view_player(ctx, name):
    player = csh.get_player(name)
    if player is not None:
        await ctx.send(player.get_player_desc())
    else:
        await ctx.send("No player exists with that name")


@bot.command(name="login", help="Login as a gremlin to show your serving status as online")
@commands.has_role("gremlin")
async def login_gremlin(ctx, name):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    role = discord.utils.get(guild.roles, id="gremlin")
    #member = [m.id for m in r.members]
    await ctx.send("test")


def start_bot():
    bot.run(TOKEN)
