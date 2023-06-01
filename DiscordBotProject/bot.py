# bot.py
import os
import re

import discord
from dotenv import load_dotenv
from discord.ext import commands

import character_sheet_handler as csh
import MapStuff
import server
from server import cc_results
from dice import roll_dice
from MapStuff import Map
from functools import reduce

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
    player_control_channels = discord.utils.get(guild.categories, id=1113212348887482458).text_channels

    gremlin_role = discord.utils.get(guild.roles, id=1112687715750785075)
    gremlins = [m.display_name for m in gremlin_role.members]
    server.load_gremlins(gremlins)
    server.load_messages()
    player_role = discord.utils.get(guild.roles, id=1113223879998046319)
    players = [m.name for m in player_role.members]
    server.load_players(players, player_channels, player_control_channels)
    csh.load_sheets()
    server.load_characters()

    server_map = Map("http://192.168.1.22:8000", "Terra")


# Permissions


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


# Behind the Curtain
@bot.event
async def on_message(message):
    channel = message.channel
    content = message.content
    if channel in player_channels and server.from_player(message) and '!' not in content:
        player = message.author.name
        await server.get_control_channel(channel).send(server.format_message(player, content))
    else:
        await bot.process_commands(message)


# Character Sheet


@bot.command(name="viewSheet", help="View a given player's character sheet \n name: the name of the character to "
                                    "view")
@commands.has_role("gremlin")
async def view_sheet(ctx, name):
    character = csh.get_character(name)
    if character is not None:
        await ctx.send(server.command_wrap(character.get_desc()))
    else:
        await ctx.send("No player exists with that name")


@bot.command(name="sheet", help="modify your character sheet")
@commands.has_role("gremlin")
async def sheet(ctx, command, name=None, *params):
    if name is None:
        name = server.get_character_from_ctrl_channel(ctx)
    if name is None:
        return await ctx.send("Please provide a name or use the command from a control channel")
    if command == "add":
        value = params[-1]
        key = params[-2]
        if len(params) > 2:
            # e.g. !sheet <soren> add inventory skull 2
            # e.g. !sheet <soren> add inventory/backpack skull 2
            # e.g. !sheet <soren> add inventory/bandolier healing_potion 1
            # e.g. !sheet <soren> add skills building 1
            target = reduce(lambda a, b: str(a) + "/" + str(b), params[1:-2], params[0])
        else:
            # e.g. !sheet <soren> add hp 10
            # e.g. !sheet <soren> add achievements murderer
            # e.g. !sheet <soren> add inventory skull
            # e.g. !sheet <soren> add inventory/backpack skull
            targets = re.split("/", key)
            target = reduce(lambda a, b: str(a) + "/" + str(b), params[1:-2], params[0])
            key = targets[-1]
        await ctx.send(csh.add_data(name, key=key, value=value, target=target))
    if command == "show":
        if len(params) == 0:
            # e.g. !sheet <soren> show
            target = None
        else:
            # e.g. !sheet <soren> show achievements
            # e.g. !sheet <soren> show backpack/bandolier
            target = reduce(lambda a, b: str(a) + "/" + str(b), params[1:], params[0])
        await cc_results(ctx, "\n"+csh.get_data(name, target))
    if command == "view":
        if len(params) == 0:
            target = None
        else:
            target = reduce(lambda a, b: str(a) + "/" + str(b), params[1:], params[0])
        await ctx.send(server.command_wrap(csh.get_data(name, target)))



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


@bot.command(name="m", help="Sends a message to the the player channel")
@commands.has_role("gremlin")
async def control_message(ctx, *args):
    message = " ".join(args)
    channel = ctx.message.channel
    player_channel = server.get_player_channel(channel)
    if player_channel is not None:
        await player_channel.send(server.format_message("Server", message))
    else:
        await ctx.send("Message failed to send")


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
    await cc_results(ctx, message)


# Movement / Map API
move_help = "Moves a given player based on the parameters \n " \
            "Player: the player to move \n" \
            "Direction: NW, N, NE, SE, S, SW, <TileID> ;(this is not case sensitive)" \
            "TileID: The tile to set a player to if the set direction is chosen"


@bot.command(name="move", help=move_help)
@commands.has_role("gremlin")
async def move(ctx, *args):
    ctx = server.set_output_channel(ctx)
    player = args[0]
    directions = args[1:]
    if player and directions:
        for direction in directions:
            if direction.isnumeric():
                await ctx.send(server_map.botMove(int(direction), player))
            else:
                await ctx.send(server_map.move_direction(player, direction.upper()))
    else:
        await ctx.send("Incorrect parameters given, please see !help command")


map_help = "Allows Editing of the Map \n " \
           "Option: label, comment, add (add player) \n" \
           "Tile: The ID of the tile to edit" \
           "Content: the content of the label, comment, or player. use delete to delete a label or comment" \
           "Option2: color for adding players, or the 'set' flag for comments/labels" \
           "*skills: any skills that need to be added as part of character creation"


@bot.command(name="map", help=map_help)
@commands.has_role("gremlin")
async def map_edit(ctx, option, tile, content, option2=None, *skills):
    if option.lower() == "add" and MapStuff.is_valid_color(option2):
        server.add_player(ctx.message.channel, content, skills)
        await ctx.send(server_map.add_player(tile, content, option2))
    elif option.lower() == "label":
        if content == "delete":
            await ctx.send(server_map.delete_label(tile, content))
        else:
            await ctx.send(server_map.set_label(tile, content))
    elif option.lower() == "comment":
        if content == "delete":
            await ctx.send(server_map.delete_comments(tile))
        elif option2 == "set":
            await ctx.send(server_map.set_comments(tile, content))
        else:
            await ctx.send(server_map.append_comments(tile, content))
    else:
        return "Incorrect parameter given, please see !help command"


# Testing

@bot.command(name="test", help="test")
@commands.has_role("bot_tester")
async def test(ctx):
    await ctx.send("test")


def start_bot():
    bot.run(TOKEN)
