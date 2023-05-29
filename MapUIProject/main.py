import ctypes

import pygame
import utils
import sys
from pygame.locals import *
import math
import requests
import ast


from tile import Tile

ipAddress = "192.168.1.22:8000"
mapName = sys.argv[1]
currentMapHash = ""


iterations = 0
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), (user32.GetSystemMetrics(1) - 80)


def distanceBetweenTwoPoints(A, B):
    return math.hypot(A[0] - B[0], A[1] - B[1])


def center(bs, camera):
    minX = 0
    maxX = 0
    minY = 0
    maxY = 0
    for b in bs:
        if b.loc[0] > maxX:
            maxX = b.loc[0]
        elif b.loc[0] < minX:
            minX = b.loc[0]
        if b.loc[1] > maxY:
            maxY = b.loc[1]
        elif b.loc[1] < minY:
            minY = b.loc[1]
    if utils.vertical:
        centerPoint = (((maxX - minX) / 2) + minX, ((maxY - minY) / 2) + minY)
        camera["ox"] = ((screensize[0] - camera["scale"]) / 2) - centerPoint[0] * camera["scale"]
        camera["oy"] = (screensize[1] / 2) - centerPoint[1] * camera["scale"] * 0.866
    else:
        centerPoint = (((maxY - minY) / 2) + minY, ((maxX - minX) / 2) + minX)
        camera["oy"] = ((screensize[0] - camera["scale"]) / 2) - centerPoint[0] * camera["scale"]
        camera["ox"] = (screensize[1] / 2) - centerPoint[1] * camera["scale"] * 0.866


pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()

CHECKHASHEVENT, t = pygame.USEREVENT+1, 10000
pygame.time.set_timer(CHECKHASHEVENT, t)


class Button:
    def __init__(self, bounds, onClick):
        self.bounds = bounds
        self.onClick = onClick

    def click(self, m_p):
        if self.bounds.collidepoint(m_p):
            self.onClick()
            return True
        else:
            return False


infoFont = pygame.font.SysFont("monospace", 30)
controlFont = pygame.font.SysFont("monospace", 60)
symbolFont = pygame.font.SysFont("monospace", 30)

buttons = []

DISPLAY_SURF = pygame.display.set_mode(screensize)
DISPLAY_SURF.fill(utils.colors["background"])
pygame.display.set_caption("Unravel Map Viewer")
scale = 100
camera = {"scale": scale,
          "ox": ((screensize[0] - scale) / 2),
          "oy": (screensize[1] / 2)}
drag = False
lastMousePos = (0, 0)
lastMouseDownPos = (0, 0)
currentSelectionIndex = 0
placementMode = False

currentFocusTile = None

mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)

currentMapHash = mapData["hash"]
Ms = []
for tile in mapData["tiles"]:
    toAppend = Tile(mapData["tiles"][tile]["location"], mapData["tiles"][tile]["type"], tile)
    neighbours = utils.find_tiles(utils.generate_neighbour_locs(mapData["tiles"][tile]["location"]), Ms)
    toAppend.neighbours = neighbours
    for n in neighbours:
        if n is not None:
            n.add_neighbour(toAppend)
    Ms.append(toAppend)

center(Ms, camera)


while True:
    leftClick = False
    rightClick = False

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                drag = True
                lastMousePos = event.pos
                lastMouseDownPos = event.pos
            elif event.button == 4:
                currentSelectionIndex -= 1
                if currentSelectionIndex < 0:
                    currentSelectionIndex = len(utils.tiles) - 1
            #    camera["scale"] += 15
            #    m_x, m_y = event.pos
            #    camera["ox"] -= ((m_x / screensize[0]) - 0.5) * 15
            #    camera["oy"] -= ((m_y / screensize[1]) - 0.5) * 15
            elif event.button == 5:
                currentSelectionIndex += 1
                if currentSelectionIndex >= len(utils.tiles):
                    currentSelectionIndex = 0
            #    camera["scale"] -= 15
            #    m_x, m_y = event.pos
            #    camera["ox"] += ((m_x / screensize[0]) - 0.5) * 15
            #    camera["oy"] += ((m_y / screensize[1]) - 0.5) * 15
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                drag = False
                if event.pos == lastMouseDownPos:
                    leftClick = True
            if event.button == 3:
                if placementMode:
                    rightClick = True
                else:
                    center(Ms, camera)
        elif event.type == MOUSEMOTION:
            if drag:
                m_x, m_y = event.pos
                if utils.vertical:
                    camera["ox"] -= lastMousePos[0] - m_x
                    camera["oy"] -= lastMousePos[1] - m_y
                else:
                    camera["oy"] -= lastMousePos[0] - m_x
                    camera["ox"] -= lastMousePos[1] - m_y
                lastMousePos = event.pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                placementMode = not placementMode
        elif event.type == CHECKHASHEVENT:
            mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)
            if currentMapHash != mapData["hash"]:
                currentMapHash = mapData["hash"]
                Ms = []
                for tile in mapData["tiles"]:
                    toAppend = Tile(mapData["tiles"][tile]["location"], mapData["tiles"][tile]["type"], tile)
                    neighbours = utils.find_tiles(utils.generate_neighbour_locs(mapData["tiles"][tile]["location"]), Ms)
                    toAppend.neighbours = neighbours
                    for n in neighbours:
                        if n is not None:
                            n.add_neighbour(toAppend)
                    Ms.append(toAppend)

    DISPLAY_SURF.fill(utils.colors["background"])
    BsBoxes = []
    lowestX = 10000
    highestX = -10000
    for b in Ms:
        if lowestX > b.loc[0]:
            lowestX = b.loc[0]
        if highestX < b.loc[0]:
            highestX = b.loc[0]
    for i in range(lowestX, highestX + 1):
        for b in Ms:
            if b.loc[0] == i:
                rect = b.get_bounds(camera)
                BsBoxes.append((rect, b))

    if placementMode:

        edgePoints = []
        for b in Ms:
            p = b.loc

            exists = False
            ox = -1
            if p[1] % 2 == 0:
                ox = 0
            pp = (p[0] + ox, p[1] - 1)
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

            exists = False
            pp = (p[0] + ox + 1, p[1] - 1)
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

            exists = False
            pp = (p[0] - 1, p[1])
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

            exists = False
            pp = (p[0] + 1, p[1])
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

            exists = False
            pp = (p[0] + ox, p[1] + 1)
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

            exists = False
            pp = (p[0] + ox + 1, p[1] + 1)
            for c in Ms:
                if c.loc[0] == pp[0] and c.loc[1] == pp[1]:
                    exists = True
                    break
            if (not exists) and (pp not in edgePoints):
                edgePoints.append(pp)

        m_x, m_y = pygame.mouse.get_pos()
        edgeBoxs = []
        hoverPoint = None
        for e in edgePoints:
            edgeBoxs.append((utils.drawCell(DISPLAY_SURF, camera, e[0], e[1], (63, 64, 69)), e))
        if len(edgeBoxs) > 0:
            closestBox = 0
            closestBoxDistance = distanceBetweenTwoPoints((m_x, m_y), edgeBoxs[0][0].center)
            for i in range(1, len(edgeBoxs)):
                dist = distanceBetweenTwoPoints((m_x, m_y), edgeBoxs[i][0].center)
                if dist < closestBoxDistance:
                    closestBoxDistance = dist
                    closestBox = i
            if edgeBoxs[closestBox][0].collidepoint((m_x, m_y)):
                hoverPoint = edgeBoxs[closestBox][1]
                utils.drawCell(DISPLAY_SURF, camera, edgeBoxs[closestBox][1][0], edgeBoxs[closestBox][1][1], (79, 80, 87))

        if hoverPoint is not None:
            toAppend = None
            if leftClick:
                toAppend = Tile(hoverPoint, utils.tiles[currentSelectionIndex], unique_id=len(Ms))
                mapData = ast.literal_eval(requests.post("http://" + ipAddress +
                                                         "/map/" + sys.argv[1] +
                                                         "/tile/" + str(toAppend.loc[0]) +
                                                         "/" + str(toAppend.loc[1]) +
                                                         "/" + toAppend.type +
                                                         "/" + str(toAppend.id) +
                                                         "/" + currentMapHash).text)
                print(mapData)
                if "message" in mapData and mapData["message"] == "This tile already exists.":
                    print("tile already there")
                else:
                    if "message" in mapData:
                        mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)
                        currentMapHash = mapData["hash"]
                        Ms = []
                        for tile in mapData["tiles"]:
                            toAppend = Tile(mapData["tiles"][tile]["location"], mapData["tiles"][tile]["type"], tile)
                            neighbours = utils.find_tiles(
                                utils.generate_neighbour_locs(mapData["tiles"][tile]["location"]), Ms)
                            toAppend.neighbours = neighbours
                            for n in neighbours:
                                if n is not None:
                                    n.add_neighbour(toAppend)
                            Ms.append(toAppend)
                        mapData = ast.literal_eval(requests.post("http://" + ipAddress +
                                                                 "/map/" + sys.argv[1] +
                                                                 "/tile/" + str(toAppend.loc[0]) +
                                                                 "/" + str(toAppend.loc[1]) +
                                                                 "/" + toAppend.type +
                                                                 "/" + str(toAppend.id) +
                                                                 "/" + currentMapHash).text)

                    if "message" not in mapData:
                        currentMapHash = mapData["hash"]
                        neighbours = utils.find_tiles(utils.generate_neighbour_locs(hoverPoint), Ms)
                        toAppend.neighbours = neighbours
                        for n in neighbours:
                            if n is not None:
                                n.add_neighbour(toAppend)
                        Ms.append(toAppend)

        lowestX = 10000
        highestX = -10000
        for b in Ms:
            if lowestX > b.loc[0]:
                lowestX = b.loc[0]
            if highestX < b.loc[0]:
                highestX = b.loc[0]
        for i in range(lowestX, highestX + 1):
            for b in Ms:
                if b.loc[0] == i:
                    rect = b.render(DISPLAY_SURF, camera)

    else:

        if leftClick:
            x = lastMouseDownPos[0]
            y = lastMouseDownPos[1]

            buttonClicked = False
            for button in buttons:
                buttonClicked = buttonClicked or button.click(lastMouseDownPos)

            if not buttonClicked:
                if len(BsBoxes) > 0:
                    closestBox = 0
                    closestBoxDistance = distanceBetweenTwoPoints((x, y), BsBoxes[0][0].center)
                    for i in range(1, len(BsBoxes)):
                        dist = distanceBetweenTwoPoints((x, y), BsBoxes[i][0].center)
                        if dist < closestBoxDistance:
                            closestBoxDistance = dist
                            closestBox = i
                    if BsBoxes[closestBox][0].collidepoint((x, y)):
                        if placementMode:
                            if BsBoxes[closestBox][1].type != "main":
                                Ms.remove(BsBoxes[closestBox][1])
                        else:
                            currentFocusTile = BsBoxes[closestBox][1]
                    else:
                        currentFocusTile = None
                else:
                    currentFocusTile = None

        lowestX = 10000
        highestX = -10000
        for b in Ms:
            if lowestX > b.loc[0]:
                lowestX = b.loc[0]
            if highestX < b.loc[0]:
                highestX = b.loc[0]
        for i in range(lowestX, highestX + 1):
            for b in Ms:
                if b.loc[0] == i:
                    rect = b.render(DISPLAY_SURF, camera, currentFocusTile == b)

    if currentFocusTile is not None:
        x = currentFocusTile.loc[0]
        y = currentFocusTile.loc[1]
        if not utils.vertical:
            x, y = y, -x
        text = ["Tile ID: " + str(currentFocusTile.id),
                "X: " + str(x) + ", Y:" + str(y),
                "Type: " + str(currentFocusTile.type)]
        barWidth, fontHeight = infoFont.size(text[0])
        fullText = text[0]
        for i in range(1, len(text)):
            w = infoFont.size(text[i])[0]
            if w > barWidth:
                barWidth = w
        utils.addAlphaRect(DISPLAY_SURF, 0, 0, barWidth + 40, screensize[1], (40, 40, 40), 160)
        for i in range(len(text)):
            utils.addText(DISPLAY_SURF, text[i], 20, 20 + (i * fontHeight), infoFont, (255, 255, 255))

    if placementMode:
        utils.addAlphaRect(DISPLAY_SURF, screensize[0] - 550, screensize[1] - 140, 550, 140, (40, 40, 40), 160)
        w = controlFont.size(utils.tiles[currentSelectionIndex])[0]
        if utils.vertical:
            pygame.draw.polygon(DISPLAY_SURF, utils.colors[utils.tiles[currentSelectionIndex].split("\\")[0]][0], utils.getHexagon(screensize[0] - 70, screensize[1] - 70, camera["scale"]))
        else:
            image = pygame.image.load("tiles/used/" + utils.tiles[currentSelectionIndex])
            image = pygame.transform.scale(image, (image.get_width() * 3.0, image.get_height() * 3.0))
            DISPLAY_SURF.blit(image, (screensize[0] - 70 - camera["scale"] * 0.5, screensize[1] - 70 - camera["scale"]))
        utils.addText(DISPLAY_SURF, utils.tiles[currentSelectionIndex], screensize[0] - 140 - w, screensize[1] - 100, controlFont,
                      (255, 255, 255))

    pygame.display.update()

    FramePerSec.tick(FPS)