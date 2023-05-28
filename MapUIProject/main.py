import ctypes

import pygame
import utils
import sys
from pygame.locals import *
import math

from tile import Tile

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
    centerPoint = (((maxX - minX) / 2) + minX, ((maxY - minY) / 2) + minY)
    camera["ox"] = ((screensize[0] - camera["scale"]) / 2) - centerPoint[0] * camera["scale"]
    camera["oy"] = (screensize[1] / 2) - centerPoint[1] * camera["scale"] * 0.866


pygame.init()
FPS = 60
FramePerSec = pygame.time.Clock()


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
placementMode = False

currentFocusTile = None

Ms = [Tile((0, 0), "forest")]
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
            # elif event.button == 4:
            #    camera["scale"] += 15
            #    m_x, m_y = event.pos
            #    camera["ox"] -= ((m_x / screensize[0]) - 0.5) * 15
            #    camera["oy"] -= ((m_y / screensize[1]) - 0.5) * 15
            # elif event.button == 5:
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
                camera["ox"] -= lastMousePos[0] - m_x
                camera["oy"] -= lastMousePos[1] - m_y
                lastMousePos = event.pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                placementMode = not placementMode

    DISPLAY_SURF.fill(utils.colors["background"])
    BsBoxes = []
    for b in Ms:
        rect = b.render(DISPLAY_SURF, camera)
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
                toAppend = Tile(hoverPoint, "desert", unique_id=len(Ms))
            if rightClick:
                toAppend = Tile(hoverPoint, "forest", unique_id=len(Ms))
            if leftClick or rightClick:
                neighbours = utils.find_tiles(utils.generate_neighbour_locs(hoverPoint), Ms)
                toAppend.neighbours = neighbours
                for n in neighbours:
                    if n is not None:
                        n.add_neighbour(toAppend)
                Ms.append(toAppend)

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

    if currentFocusTile is not None:
        currentFocusTile.render(DISPLAY_SURF, camera, True)
        text = ["Tile ID: " + str(currentFocusTile.id),
                "X: " + str(currentFocusTile.loc[0]) + ", Y:" + str(currentFocusTile.loc[1]),
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

    pygame.display.update()

    FramePerSec.tick(FPS)
