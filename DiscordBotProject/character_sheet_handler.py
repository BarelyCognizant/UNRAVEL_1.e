import os
from character_sheet import load_file, Player

path = "./Backups/Players/"
players = [Player(data=load_file(file)) for file in os.listdir(path)]
