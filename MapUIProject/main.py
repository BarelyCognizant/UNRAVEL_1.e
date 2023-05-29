import ctypes
import pygame
import sys
from pygame.locals import *
import math
import requests
import ast
import textwrap
import utils


from tile import Tile
from player import Player

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
utils.setFonts()
FPS = 60
FramePerSec = pygame.time.Clock()

CHECKHASHEVENT, t = pygame.USEREVENT+1, 10000
pygame.time.set_timer(CHECKHASHEVENT, t)


class PaletteButton:
    def __init__(self, bounds, paletteName):
        self.bounds = bounds
        self.paletteName = paletteName

    def click(self, m_p):
        global currentPalette
        global currentSelectionIndex
        if self.bounds.collidepoint(m_p):
            currentPalette = self.paletteName
            while utils.tiles[currentSelectionIndex].split("\\")[0] != currentPalette:
                currentSelectionIndex += 1
                if currentSelectionIndex >= len(utils.tiles):
                    currentSelectionIndex = 0
            return True
        else:
            return False


buttons = []

w = 0
for palette in utils.palettes:
    tw = utils.labelFont.size(palette)[0]
    if tw > w:
        w = tw
count = -1
for palette in utils.palettes:
    count += 1
    buttons.append(PaletteButton(pygame.Rect(screensize[0] - w - 40, screensize[1] - 190 - (50 * count), w + 40, 40), palette))

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
currentSelectionIndex = 5
currentPalette = "grass"
placementMode = False

currentFocusTile = None

mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)

currentMapHash, Ms, Ps = utils.updateData(mapData)

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
                while utils.tiles[currentSelectionIndex].split("\\")[0] != currentPalette:
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
                while utils.tiles[currentSelectionIndex].split("\\")[0] != currentPalette:
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
                currentMapHash, Ms, Ps = utils.updateData(mapData)

    characterPerspective = "Soren"
    if characterPerspective != "":
        centerId = mapData["players"][characterPerspective]["tileId"]
        centerTile = ""
        for m in Ms:
            m.visible = False
            m.distance = -1
            if m.id == centerId:
                m.visible = True
                m.distance = 0
                centerTile = m
        visionDistance = 2
        for i in range(1, visionDistance + 1):
            tilesToChange = []
            for m in Ms:
                if m.distance == -1:
                    neighboursInView = []
                    for n in m.neighbours:
                        if n.visible:
                            neighboursInView.append(n)
                    minDistance = 1000
                    for n in neighboursInView:
                        if m.height > centerTile.height:
                            if m.height > n.height:
                                if centerTile.covered:
                                    if not n.covered or n.distance == 0:
                                        minDistance = min(n.distance + 1, minDistance)
                                else:
                                    minDistance = min(n.distance + 1, minDistance)
                        else:
                            if m.height >= n.height:
                                if centerTile.covered:
                                    if not n.covered or n.distance == 0:
                                        minDistance = min(n.distance + 1, minDistance)
                                else:
                                    minDistance = min(n.distance + 1, minDistance)
                            else:
                                if m.height < centerTile.height:
                                    minDistance = min(n.distance + 1, minDistance)
                    if minDistance <= visionDistance:
                        tilesToChange.append((m, minDistance))
            for m in tilesToChange:
                m[0].visible = True
                m[0].distance = m[1]
    else:
        for m in Ms:
            m.visible = True

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

        x = lastMouseDownPos[0]
        y = lastMouseDownPos[1]

        buttonClicked = False
        for button in buttons:
            buttonClicked = buttonClicked or button.click(lastMouseDownPos)

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
        allBoxs = edgeBoxs + BsBoxes
        edge = False
        if len(allBoxs) > 0:
            closestBox = 0
            closestBoxDistance = distanceBetweenTwoPoints((m_x, m_y), allBoxs[0][0].center)
            for i in range(1, len(allBoxs)):
                dist = distanceBetweenTwoPoints((m_x, m_y), allBoxs[i][0].center)
                if dist < closestBoxDistance:
                    closestBoxDistance = dist
                    closestBox = i
            if allBoxs[closestBox][0].collidepoint((m_x, m_y)):
                hoverPoint = allBoxs[closestBox][1]
                if closestBox < len(edgeBoxs):
                    edge = True
                    utils.drawCell(DISPLAY_SURF, camera, allBoxs[closestBox][1][0], allBoxs[closestBox][1][1], (79, 80, 87))

        if hoverPoint is not None and not buttonClicked:
            toAppend = None
            if leftClick and edge:
                toAppend = Tile(hoverPoint, utils.tiles[currentSelectionIndex], unique_id=mapData["idCount"])
                mapData = ast.literal_eval(requests.post("http://" + ipAddress +
                                                         "/map/" + sys.argv[1] +
                                                         "/tile/" + str(toAppend.loc[0]) +
                                                         "/" + str(toAppend.loc[1]) +
                                                         "/" + toAppend.type +
                                                         "/" + str(toAppend.id) +
                                                         "/" + currentMapHash).text)
                if "message" in mapData and mapData["message"] == "This tile already exists.":
                    print("tile already there")
                else:
                    if "message" in mapData:
                        mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)
                        currentMapHash, Ms, Ps = utils.updateData(mapData)
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
            elif rightClick and not edge:
                empty = True
                for p in Ps:
                    if p.loc == hoverPoint.id:
                        empty = False
                        break
                if empty:
                    mapData = ast.literal_eval(requests.delete("http://" + ipAddress +
                                                             "/map/" + sys.argv[1] +
                                                             "/tile/" + str(hoverPoint.id) +
                                                             "/" + currentMapHash).text)
                    if "message" in mapData and mapData["message"] == "This tile does not exist.":
                        print("tile already gone")
                    else:
                        if "message" in mapData:
                            mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)

                            currentMapHash, Ms, Ps = utils.updateData(mapData)
                            mapData = ast.literal_eval(requests.delete("http://" + ipAddress +
                                                             "/map/" + sys.argv[1] +
                                                             "/tile/" + str(hoverPoint.id) +
                                                             "/" + currentMapHash).text)
                        if "message" not in mapData:
                            currentMapHash, Ms, Ps = utils.updateData(mapData)
            elif leftClick and not edge:
                newType = utils.tiles[currentSelectionIndex]
                mapData = ast.literal_eval(requests.put("http://" + ipAddress +
                                                           "/map/" + sys.argv[1] +
                                                           "/tile/" + newType +
                                                           "/" + str(hoverPoint.id) +
                                                           "/" + currentMapHash).text)
                if "message" in mapData and mapData["message"] == "This tile does not exist.":
                    print("tile already gone")
                else:
                    if "message" in mapData:
                        mapData = ast.literal_eval(requests.get("http://" + ipAddress + "/map/" + sys.argv[1]).text)

                        currentMapHash, Ms, Ps = utils.updateData(mapData)
                        mapData = ast.literal_eval(requests.put("http://" + ipAddress +
                                                                "/map/" + sys.argv[1] +
                                                                "/tile/" + newType +
                                                                "/" + str(hoverPoint.id) +
                                                                "/" + currentMapHash).text)

                    if "message" not in mapData:
                        currentMapHash, Ms, Ps = utils.updateData(mapData)
    else:

        if leftClick:
            x = lastMouseDownPos[0]
            y = lastMouseDownPos[1]

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
                if placementMode:
                    b.render(DISPLAY_SURF, camera)
                else:
                    if b.visible:
                        b.render(DISPLAY_SURF, camera, currentFocusTile == b)
    for i in range(lowestX, highestX + 1):
        for b in Ms:
            if b.loc[0] == i:
                playersInLocation = []
                for p in Ps:
                    if p.loc == b.id:
                        playersInLocation.append(p)
                for j in reversed(range(len(playersInLocation))):
                    playersInLocation[j].render(DISPLAY_SURF, camera, Ms, j + 1)
    for i in range(lowestX, highestX + 1):
        for b in Ms:
            if b.loc[0] == i:
                b.renderLabels(DISPLAY_SURF, camera)

    if not placementMode:
        if currentFocusTile is not None:
            x = currentFocusTile.loc[0]
            y = currentFocusTile.loc[1]
            if not utils.vertical:
                x, y = y, -x
            text = [
                "Tile ID: " + str(currentFocusTile.id),
                "X: " + str(x) + ", Y:" + str(y),
                "Type: " + str(currentFocusTile.type),
                "Label: " + currentFocusTile.label,
                "",
                "Players:"
            ]

            for p in Ps:
                if p.loc == currentFocusTile.id:
                    text.append(p.name)

            text.append("")
            text.append("Comments: ")
            wrapper = textwrap.TextWrapper(width=30)
            wrappedComments = wrapper.wrap(currentFocusTile.comments)
            text = text + wrappedComments

            barWidth, fontHeight = utils.infoFont.size(text[0])
            fullText = text[0]
            for i in range(1, len(text)):
                w = utils.infoFont.size(text[i])[0]
                if w > barWidth:
                    barWidth = w
            utils.addAlphaRect(DISPLAY_SURF, 0, 0, barWidth + 40, screensize[1], (40, 40, 40), 160)
            for i in range(len(text)):
                utils.addText(DISPLAY_SURF, text[i], 20, 20 + (i * fontHeight), utils.infoFont, (255, 255, 255))

    if placementMode:
        w = utils.controlFont.size(utils.tiles[currentSelectionIndex])[0]
        utils.addAlphaRect(DISPLAY_SURF, screensize[0] - 160 - w, screensize[1] - 140, 160 + w, 140, (40, 40, 40), 160)
        if utils.vertical:
            pygame.draw.polygon(DISPLAY_SURF, utils.colors[utils.tiles[currentSelectionIndex].split("\\")[0]][0], utils.getHexagon(screensize[0] - 70, screensize[1] - 70, camera["scale"]))
        else:
            image = pygame.image.load("tiles/used/" + utils.tiles[currentSelectionIndex])
            image = pygame.transform.scale(image, (image.get_width() * 3.0, image.get_height() * 3.0))
            DISPLAY_SURF.blit(image, (screensize[0] - 70 - camera["scale"] * 0.5, screensize[1] - 70 - camera["scale"]))
        utils.addText(DISPLAY_SURF, utils.tiles[currentSelectionIndex], screensize[0] - 140 - w, screensize[1] - 100, utils.controlFont, (255, 255, 255))

        w = 0
        for palette in utils.palettes:
            tw = utils.labelFont.size(palette)[0]
            if tw > w:
                w = tw
        count = -1
        for palette in utils.palettes:
            count += 1
            color = 40
            if currentPalette == palette:
                color = 100
            utils.addAlphaRect(DISPLAY_SURF, screensize[0] - w - 40, screensize[1] - 190 - (50 * count), w + 40, 40, (color, color, color), 160)
            utils.addText(DISPLAY_SURF, palette, screensize[0] - utils.labelFont.size(palette)[0] - 20, screensize[1] - 185 - (50 * count), utils.labelFont, (255, 255, 255))

    pygame.display.update()

    FramePerSec.tick(FPS)
