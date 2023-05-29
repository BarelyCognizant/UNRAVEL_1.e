# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

import character_sheet_handler as csh
import server
from dice import roll_dice
from MapStuff import MapStuff as Map

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

status_channel = None
player_channels = []
server_map = None


@bot.event
async def on_ready():
    global status_channel
    global player_channels
    global server_map
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    status_channel = [channel for channel in guild.channels if channel.name == "server-status"][0]
    player_rooms = discord.utils.get(guild.categories, id=1112766611963772989)
    player_channels = player_rooms.text_channels

    gremlin_role = discord.utils.get(guild.roles, id=1112687715750785075)
    gremlins = [m.display_name for m in gremlin_role.members]
    server.load_gremlins(gremlins)
    server.load_messages()

    server_map = Map()


# Permissions


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


# Character Sheet


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


# Login/Status

@bot.command(name="login", help="Login as a gremlin to show your serving status as online")
@commands.has_role("gremlin")
async def login_gremlin(ctx):
    await status_channel.send(server.login_gremlin(ctx.author))


@bot.command(name="logout", help="Logout as a gremlin to show your serving status as offline")
@commands.has_role("gremlin")
async def logout_gremlin(ctx):
    await status_channel.send(server.logout_gremlin(ctx.author))


# Server Messages

@bot.command(name="serverMessage", help="Sends a server message, or uses a previously stored shorthand \n Options: all")
@commands.has_role("gremlin")
async def server_message(ctx, message, option=None, name=None):
    if option == "all":
        for channel in player_channels:
            await channel.send(server.message(message))
    elif option == "add" and name:
        server.add_message(name, message)
        await ctx.send("Message shortcut successfully saved as: " + name)
    else:
        await ctx.send(server.message(message))


# Dice


@bot.command(name="roll", help="Roll x dice")
async def roll(ctx, *args):
    num = int(args[0])
    struggle = int(args[1]) if len(args) > 1 else None
    if struggle:
        result = roll_dice(num, struggle)
        message = "Rolling: [" + str(result[0]) + "/" + str(num + struggle) + "] \n" + str(result[1]) \
                  + " Threats Rolled"
    else:
        result = roll_dice(num)
        message = "Rolling: [" + str(result[0]) + "/" + str(num) + "]"
    await ctx.send(message)


# Movement
move_help = "Moves a given player based on the parameters \n " \
            "Player: the player to move \n" \
            "Direction: NW, N, NE, SE, S, SW, <TileID> ;(this is not case sensitive)" \
            "TileID: The tile to set a player to if the set direction is chosen"


@bot.command(name="move", help=move_help)
@commands.has_role("gremlin")
async def move(ctx, player, direction):
    if direction.isnumeric():
        await ctx.send(server_map.botMove(int(direction), player))
    else:
        await ctx.send(server_map.move_direction(player, direction.upper()))


# Testing

@bot.command(name="test", help="test")
@commands.has_role("bot_tester")
async def test(ctx):
    await ctx.send("test")


def start_bot():
    bot.run(TOKEN)
