import os
from character_sheet import Character
import re

path = "./Backups/Characters/"
sheets = []


def load_sheets():
    if len(sheets) == 0:
        [sheets.append(Character(filepath=path + file)) for file in os.listdir(path)]


def get_sheets():
    return sheets


def get_character(name):
    matches = [character for character in sheets if name == character.data["Name"]]
    if len(matches) > 0:
        return matches[0]
    else:
        return None


def add_new_character(name, player, skill_list):
    character = Character(player=player, name=name, skill_list=skill_list)
    character.save_to_file(path + name)
    sheets.append(character)
    return "Character Created Successfully"


# name: character name
# target: the place to add the data, if None, adds it to the root of the sheet
# TODO: check the character object updates properly (referencing is hard)
def add_data(name, key, value, target=None):
    character = get_character(name)
    if character is not None:
        return character.add_data(target=target, key=key, value=value)
    else:
        return "could not find character " + name


def remove_data(name, key, target=None):
    character = get_character(name)
    if character:
        string = character.remove_data(target, key)
        return "removed " + string
    else:
        return "could not find character " + name


def move_data(name, key, source=None, target=None):
    character = get_character(name)
    if character:
        data = character.get_data(target=source, key=key)
        character.remove_data(target=source, key=key)
        return character.add_data(target=target, key=key, value=data)
    else:
        return "could not find character " + name


# name: character name
# target: the place to add the data, if None, adds it to the root of the sheet
def find_data(name, target):
    character = get_character(name)
    if character is None:
        raise RuntimeError("could not find character " + name)
    if target is not None:
        data_path = re.split("/", target)
        data = character.get_data()
        for s in data_path:
            if s in data:
                data = data[s]
            else:
                raise RuntimeError("data path " + target + " failed to find " + s)
        return data, data_path, character
    else:
        raise RuntimeError("data path is None")


# name: character name
# target: where to find the target data "target/subtarget/subsubtarget", if None will return all data
def get_data(name, target=None):
    if target is not None:
        try:
            data, data_path, character = find_data(name, target)
        except RuntimeError as e:
            return e
        return character.get_desc(key=data_path[-1], value=data)
    else:
        character = get_character(name)
        if character is not None:
            return character.get_desc()
        else:
            return "could not find character " + name
