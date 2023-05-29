import random

DICE = [0, 0, 0, 0, 1, 1]
STRUGGLEDICE = [0, 0, 0, 1, 1, 2]


def roll_dice(skill, struggle=0):
    succ = 0
    succ += struggle
    threats = 0
    for i in range(skill):
        succ += random.choice(DICE)
    for i in range(struggle):
        threats += random.choice(STRUGGLEDICE)
    return succ, threats
