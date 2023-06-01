import os
from character_sheet import save_file, load_file
import character_sheet_handler as csh

gremlins = []
online_gremlins = []
message_shortcuts = {"test": "This is an Automated Server Test Message. \n Please Ignore."}
path = "./Backups/Server/messages.json"

player_channels = {}
player_channels_reverse = {}
bound_channels = {}
bound_channels_reverse = {}

player_characters = {}


def login_gremlin(name):
    online_gremlins.append(name)
    return "Server Update: Server online at " + str(len(online_gremlins)) + "/" + str(len(gremlins)) + " capacity."


def logout_gremlin(name):
    online_gremlins.remove(name)
    if len(online_gremlins) > 0:
        return "Server Update: Server online at " + str(len(online_gremlins)) + "/" + str(len(gremlins)) + " capacity."
    else:
        return "Server Update: Server is going offline."


def load_gremlins(gremlin_list):
    gremlins.append(gremlin_list)


def load_players(players, channels, control_channels):
    for channel in channels:
        control_channel = [c for c in control_channels if str(channel.name) in str(c.name)]
        if len(control_channel) > 0:
            bound_channels[channel] = control_channel[0]
            bound_channels_reverse[control_channel[0]] = channel
        for member in channel.members:
            player = [player for player in players if player == member.name]
            if len(player) > 0:
                player_channels[player[0]] = channel
                player_channels_reverse[channel] = player[0]
    """print(player_channels)
    print(player_channels_reverse)
    print(bound_channels)
    print(bound_channels_reverse)"""
    return player_channels


def load_characters():
    sheets = csh.get_sheets()
    for sheet in sheets:
        character = sheet.data["Name"]
        player = sheet.data["Player"]
        player_characters[player] = character


def get_players():
    return player_channels


def from_player(sent_message):
    return sent_message.author.name in player_channels


def get_channel(player):
    return player_channels[player]


def get_control_channel(player_channel):
    return bound_channels[player_channel]


def get_player_channel(control_channel):
    return bound_channels_reverse[control_channel]


def set_output_channel(ctx):
    channel = ctx.message.channel
    return bound_channels_reverse[channel] if channel in bound_channels_reverse else ctx


def get_player_from_context(ctx):
    ctrl_channel = ctx.message.channel
    return player_channels_reverse[bound_channels_reverse[ctrl_channel]]


def get_character_from_ctrl_channel(ctx):
    return player_characters[get_player_from_context(ctx)] if ctx.message.channel in bound_channels_reverse else None


def get_character_from_player(player):
    return player_channels[player]


def add_player(ctrl_channel, character, skills=None):
    if skills is None:
        skills = []
    player = player_channels_reverse[bound_channels_reverse[ctrl_channel]]
    player_characters[player] = character
    csh.add_new_character(character, player, skills)


async def cc_results(ctx, results):
    channel = ctx.message.channel
    if channel in bound_channels_reverse:
        await bound_channels_reverse[channel].send(format_message("server", results))
    return await ctx.send(command_wrap(results))


def get_player_channel_old(control_channel):
    for channel in bound_channels:
        if bound_channels[channel] == control_channel:
            return channel
    return None


def format_message(player, content):
    return command_wrap(player + " :: " + content)


def command_wrap(text):
    return "```" + text + "```"


def message(text):
    if text in message_shortcuts:
        server_message = message_shortcuts[text]
    else:
        server_message = text
    return command_wrap(server_message)


def add_message(name, text):
    message_shortcuts[name] = text
    save_file(path, message_shortcuts)


def remove_message(name):
    message_shortcuts.pop(name)
    save_file(path, message_shortcuts)


def load_messages():
    global message_shortcuts
    if os.path.exists(path):
        message_shortcuts = load_file(path)
