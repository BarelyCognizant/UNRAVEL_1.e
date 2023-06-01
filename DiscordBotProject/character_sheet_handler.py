import os
from character_sheet import load_file, Player
import re

path = "./Backups/Players/"
sheets = []


def load_sheets():
    sheets.append([Player(filepath=path + file) for file in os.listdir(path)])


def get_player(name):
    matches = [player for player in sheets if name == player.get_data["name"]]
    if len(matches) == 0:
        return matches[0]
    else:
        return None


def add_new_player(name):
    player = Player(name=name)
    sheets.append(player)
    return "Player Created Successfully"


# name: player name
# target: the place to add the data, if None, adds it to the root of the sheet
# TODO: check the player object updates properly (referencing is hard)
def add_data(name, key, value, target=None):
    player = get_player(name)
    if player is not None:
        return player.add_data(target=target, key=key, value=value)
    else:
        return "could not find player " + name


def remove_data(name, key, target=None):
    player = get_player(name)
    if player:
        string = player.remove_data(target, key)
        return "removed " + string
    else:
        return "could not find player " + name


def move_data(name, key, source=None, target=None):
    player = get_player(name)
    if player:
        data = player.get_data(target=source, key=key)
        player.remove_data(target=source, key=key)
        return player.add_data(target=target, key=key, value=data)
    else:
        return "could not find player " + name


# name: player name
# target: the place to add the data, if None, adds it to the root of the sheet
def find_data(name, target):
    player = get_player(name)
    if player is None:
        raise RuntimeError("could not find player " + name)
    if target is not None:
        data_path = re.split("/", target)
        data = player.get_data()
        for s in data_path:
            if s in data:
                data = data[s]
            else:
                raise RuntimeError("data path " + data_path + " failed to find " + s)
        return data, data_path, player
    else:
        raise RuntimeError("data path is None")


# name: player name
# target: where to find the target data "target/subtarget/subsubtarget", if None will return all data
def get_data(name, target=None):
    if target is not None:
        try:
            data, data_path, player = find_data(name, target)
        except RuntimeError as e:
            return e
        return player.get_desc(key=data_path[-1], value=data)
    else:
        player = get_player(name)
        if player is not None:
            return player.get_desc()
        else:
            return "could not find player " + name
