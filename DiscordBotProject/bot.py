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


@bot.command(name="create_player", help="Create an Empty Player")
@commands.has_role("bot_tester")
async def test(ctx):
    csh.Player.generateBasePlayer()
    await ctx.send("Player Created")


@bot.command(name="view_player", help="view a given player's character sheet")
@commands.has_role("bot_tester")
async def test(ctx):
    csh.Player.generateBasePlayer()
    await ctx.send("Player Created")






def start_bot():
    bot.run(TOKEN)
