import os
from character_sheet import load_file, Player

path = "./Backups/Players/"
players = [Player(data=load_file(file)) for file in os.listdir(path)]


def get_player(name):
    return [player for player in players if name.equals(player.name())][0]


def add_new_player(name):
    player = Player(name)
    players.append(player)
    return "Player Created Successfully"
