import pygame
import glob
import csv

import renderer
from tile import Tile
from player import Player

infoFont = ""
controlFont = ""
labelFont = ""
cloudScale = 600
weatherOn = True

ipAddress = "192.168.1.22:8000"


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
    "background": (53, 54, 58)
}

tilePaths = glob.glob("..\\MapUIProject\\tiles\\used/*/*.png")
for i in range(0, len(tilePaths)):
    tilePaths[i] = tilePaths[i][len("..\\MapUIProject\\tiles\\used\\"):]
tiles = tilePaths

palettes = []
for tile in tiles:
    palettes.append(tile.split("\\")[0])
palettes = list(dict.fromkeys(palettes))

metadata = {}
with open("..\\MapUIProject\\tiles\\used\\tile_metadata.txt", "r", encoding="utf8") as metadata_file:
    tsv_reader = csv.reader(metadata_file, delimiter="\t")
    for row in tsv_reader:
        (type, covered, height) = row
        covered = covered == "True"
        height = int(height)
        metadata[type] = {"covered": covered, "height": height}

region_metadata = {}
with open("..\\MapUIProject\\tiles\\used\\region_metadata.txt", "r", encoding="utf8") as metadata_file:
    tsv_reader = csv.reader(metadata_file, delimiter="\t")
    for row in tsv_reader:
        (region, rain_threshold, cloud_threshold) = row
        rain_threshold = float(rain_threshold)
        cloud_threshold = float(cloud_threshold)
        region_metadata[region] = {"rain_threshold": rain_threshold, "cloud_threshold": cloud_threshold}

dryClouds = []
for i in range(1, 4):
    dryClouds.append("..\\MapUIProject\\clouds\\dry\\cloud" + str(i) + ".png")


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
    image = pygame.transform.scale(image, (image.get_width() * 0.03 * camera["scale"], image.get_height() * 0.03 * camera["scale"]))
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


def drawCloud(surface, camera, x, y, image):
    x = (x * (camera["scale"] + cloudScale)) + camera["ox"]
    y = (y * (camera["scale"] + cloudScale) * 0.866) + camera["oy"]
    x, y = y, x
    image = pygame.transform.scale(image, (image.get_width() * 1.8, image.get_height() * 1.8))
    surface.blit(image, (x - (image.get_width() / 2), y - (image.get_height() / 2)))


_circle_cache = {}


def circlePoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def drawLabel(surface, camera, x, y, label, color):
    outlineColor = (200, 200, 200)
    if color == (255, 255, 255):
        outlineColor = (0, 0, 0)

    if (y % 2) == 0:
        x = x + 0.5
    x = (x * camera["scale"]) + camera["ox"]
    y = (y * camera["scale"] * 0.866) + camera["oy"]
    if not vertical:
        x, y = y, x
    width = labelFont.size(label)[0]

    opx = 2
    textSurface = labelFont.render(label, True, color).convert_alpha()
    w = textSurface.get_width() + 2 * opx
    h = labelFont.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(labelFont.render(label, True, outlineColor).convert_alpha(), (0, 0))

    for dx, dy in circlePoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textSurface, (opx, opx))

    surface.blit(surf, (x - (width / 2), y + 20))


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
        locAsTuple = (b.loc[0], b.loc[1])
        if locAsTuple in locs:
            ret.append(b)
    return ret


def updateData(mapData, camera=None):
    currentMapHash = mapData["hash"]
    Ms = []
    for tile in mapData["tiles"]:
        toAppend = Tile(mapData["tiles"][tile]["location"], mapData["tiles"][tile]["type"], tile,
                        mapData["tiles"][tile]["label"], mapData["tiles"][tile]["comments"],
                        mapData["tiles"][tile]["description"])
        neighbours = find_tiles(generate_neighbour_locs(mapData["tiles"][tile]["location"]), Ms)
        toAppend.neighbours = neighbours
        for n in neighbours:
            n.add_neighbour(toAppend)
        Ms.append(toAppend)
    Ps = []
    for player in mapData["players"]:
        Ps.append(Player(player, mapData["players"][player]["tileId"], mapData["players"][player]["color"], True))
    for npc in mapData["npcs"]:
        Ps.append(Player(npc, mapData["npcs"][npc]["tileId"], mapData["npcs"][npc]["color"], False))
    if camera is not None:
        renderer.update_clouds(Ms, camera)
    return currentMapHash, Ms, Ps


def convertToGreyscale(surf):
    width, height = surf.get_size()
    for x in range(width):
        for y in range(height):
            red, green, blue, alpha = surf.get_at((x, y))
            average = (red + green + blue) // 3
            gs_color = (average, average, average, alpha)
            surf.set_at((x, y), gs_color)
    return surf
