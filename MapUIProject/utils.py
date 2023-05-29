import pygame
import glob

from tile import Tile
from player import Player

infoFont = ""
controlFont = ""
labelFont = ""


def setFonts():
    global infoFont
    global controlFont
    global labelFont
    infoFont = pygame.font.SysFont("monospace", 30)
    controlFont = pygame.font.SysFont("monospace", 60)
    labelFont = pygame.font.SysFont("monospace", 30, bold=True)


colors = {
    "desert": [(201, 173, 71), (232, 212, 139)],
    "grass": [(83, 171, 79), (120, 207, 116)],
    "ocean": [(41, 108, 217), (78, 131, 217)],
    "snow": [(197, 206, 219), (255, 255, 255)],
    "settlement": [(84, 84, 84), (120, 120, 120)],
    "background": (53, 54, 58),
    "red": (255, 0, 0),
    "orange": (255, 98, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "lightblue": (0, 255, 255),
    "blue": (0, 0, 255),
    "purple": (119, 0, 255),
    "pink": (255, 0, 255)
}

tilePaths = glob.glob("tiles\\used/*/*.png")
for i in range(0, len(tilePaths)):
    tilePaths[i] = tilePaths[i][len("tiles\\used\\"):]

tiles = tilePaths

vertical = False


def getHexagon(x, y, w):
    if vertical:
        points = [
            (x + (+0.000 * w * 0.5), y + (+1.000 * w * 0.5)),
            (x + (+0.866 * w * 0.5), y + (+0.500 * w * 0.5)),
            (x + (+0.866 * w * 0.5), y + (-0.500 * w * 0.5)),
            (x + (+0.000 * w * 0.5), y + (-1.000 * w * 0.5)),
            (x + (-0.866 * w * 0.5), y + (-0.500 * w * 0.5)),
            (x + (-0.866 * w * 0.5), y + (+0.500 * w * 0.5))
        ]
    else:
        points = [
            (x + (+1.000 * w * 0.5), y + (+0.000 * w * 0.5)),
            (x + (+0.500 * w * 0.5), y + (+0.866 * w * 0.5)),
            (x + (-0.500 * w * 0.5), y + (+0.866 * w * 0.5)),
            (x + (-1.000 * w * 0.5), y + (+0.000 * w * 0.5)),
            (x + (-0.500 * w * 0.5), y + (-0.866 * w * 0.5)),
            (x + (+0.500 * w * 0.5), y + (-0.866 * w * 0.5))
        ]
    return points


def getRect(x, y, w):
    return pygame.Rect(x - (w * 0.5), y - (w * 0.5), w, w)


def drawTile(surface, camera, x, y, image):
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    if not vertical:
        x, y = y, x
    image = pygame.transform.scale(image, (image.get_width() * 3.0, image.get_height() * 3.0))
    rect = getRect(x, y, camera["scale"])
    surface.blit(image, (x - camera["scale"] * 0.5, y - camera["scale"]))
    return rect


def getBounds(camera, x, y):
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    if not vertical:
        x, y = y, x
    rect = getRect(x, y, camera["scale"])
    return rect


def drawCell(surface, camera, x, y, color):
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    if not vertical:
        x, y = y, x
    rect = pygame.draw.polygon(surface, color, getHexagon(x, y, camera["scale"]))
    return rect


def drawLabel(surface, camera, x, y, label):
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    if not vertical:
        x, y = y, x
    w = labelFont.size(label)[0]
    addText(surface, label, x - (w / 2), y + 20, labelFont, (255, 255, 255))


def screenToCameraTransform(p, camera):
    x = p[0]
    y = p[1]
    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    return x, y


def addAlphaRect(surface, x, y, w, h, color, a):
    s = pygame.Surface((w, h))
    s.set_alpha(a)
    s.fill(color)
    surface.blit(s, (x, y))


def addText(surface, text, x, y, font, color):
    label = font.render(text, 1, color)
    surface.blit(label, (x, y))


def generate_neighbour_locs(loc):
    x = loc[0]
    y = loc[1]
    ys = [y + 1, y + 1, y, y, y - 1, y - 1]
    if y % 2 == 0:
        return [(x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x, y+1), (x+1, y+1)]
    else:
        return [(x-1, y - 1), (x, y - 1), (x - 1, y), (x + 1, y), (x-1, y + 1), (x, y + 1)]


def find_tiles(locs, bs):
    ret = []
    for b in bs:
        if b.loc in locs:
            ret.append(b)
    return ret


def updateData(mapData):
    currentMapHash = mapData["hash"]
    Ms = []
    for tile in mapData["tiles"]:
        toAppend = Tile(mapData["tiles"][tile]["location"], mapData["tiles"][tile]["type"], tile,
                        mapData["tiles"][tile]["label"], mapData["tiles"][tile]["comments"])
        neighbours = find_tiles(generate_neighbour_locs(mapData["tiles"][tile]["location"]), Ms)
        toAppend.neighbours = neighbours
        for n in neighbours:
            if n is not None:
                n.add_neighbour(toAppend)
        Ms.append(toAppend)
    Ps = []
    for player in mapData["players"]:
        Ps.append(Player(player, mapData["players"][player]["tileId"], mapData["players"][player]["color"]))
    return currentMapHash, Ms, Ps
