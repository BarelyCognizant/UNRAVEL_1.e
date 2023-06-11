import ast

import pygame
import requests
import random
import numpy as np
import math

import utils

from perlin_noise import PerlinNoise


def rtpairs(r):
    for i in range(r + 1):
        for j in range(max(i * 5, 1)):
            yield i / 10.0, j * (2 * np.pi / max(i * 5, 1))


def distanceBetweenTwoPoints(A, B):
    return math.hypot(A[0] - B[0], A[1] - B[1])


offset = 0.06

cloudNodePoints = []


def render_screen(surface, tiles, players, camera, placementMode = False, currentFocusTile = None):
    lowestX = 10000
    highestX = -10000
    for tile in tiles:
        if lowestX > tile.loc[0]:
            lowestX = tile.loc[0]
        if highestX < tile.loc[0]:
            highestX = tile.loc[0]
    for i in range(lowestX, highestX + 1):
        for tile in tiles:
            if tile.loc[0] == i:
                if placementMode:
                    tile.render(surface, camera)
                else:
                    tile.render(surface, camera, currentFocusTile == tile)
    for i in range(lowestX, highestX + 1):
        for tile in tiles:
            if tile.loc[0] == i:
                if tile.visible:
                    playersInLocation = []
                    for player in players:
                        if player.loc == tile.id:
                            playersInLocation.append(player)
                    for j in reversed(range(len(playersInLocation))):
                        playersInLocation[j].render(surface, camera, tiles, j + 1)
    random.seed(100)
    if utils.weatherOn:
        for i in range(lowestX, highestX + 1):
            for tile in tiles:
                if tile.loc[0] == i:
                    tile.renderWeather(surface, camera)
    for i in range(lowestX, highestX + 1):
        for tile in tiles:
            if tile.loc[0] == i:
                tile.renderLabels(surface, camera)


def render_full_screen(surface, tiles, players, camera, placementMode=False, currentFocusTile=None, seed=1, scroll=0):
    for tile in tiles:
        tile.visible = True

    tiles = calculateWeather(tiles, camera, seed, scroll)
    render_screen(surface, tiles, players, camera, placementMode, currentFocusTile)


def calculate_vision(tiles, centerId):
    newVisibleTiles = []

    centerTile = None
    for tile in tiles:
        tile.visible = False
        tile.distance = -1
        if tile.id == centerId:
            newVisibleTiles.append(tile)
            tile.visible = True
            tile.distance = 0
            centerTile = tile
    visionDistance = 2
    if centerTile.weather == "SNOW":
        visionDistance = 0
    for i in range(1, visionDistance + 1):
        tilesToChange = []
        for tile in tiles:
            if tile.distance == -1:
                neighboursInView = []
                for n in tile.neighbours:
                    if n.visible:
                        neighboursInView.append(n)
                minDistance = 1000
                for n in neighboursInView:
                    if n.weather != "RAIN" or n.id == centerTile.id:
                        if tile.height > centerTile.height:
                            if tile.height > n.height:
                                if centerTile.covered:
                                    if not n.covered or n.distance == 0:
                                        minDistance = min(n.distance + 1, minDistance)
                                else:
                                    minDistance = min(n.distance + 1, minDistance)
                        else:
                            if tile.height >= n.height:
                                if centerTile.covered:
                                    if not n.covered or n.distance == 0:
                                        minDistance = min(n.distance + 1, minDistance)
                                else:
                                    minDistance = min(n.distance + 1, minDistance)
                            else:
                                if tile.height < centerTile.height:
                                    minDistance = min(n.distance + 1, minDistance)
                if minDistance <= visionDistance:
                    tilesToChange.append((tile, minDistance))
        for tile in tilesToChange:
            tile[0].visible = True
            tile[0].distance = tile[1]
            newVisibleTiles.append(tile[0])

    return tiles, newVisibleTiles


def render_perspective(surface, tiles, players, camera, centerId):
    tiles, _ = calculate_vision(tiles, centerId)
    render_screen(surface, tiles, players, camera)


def get_map_image_by_tile(mapName, tileId, size, player=False, tiles=[], Ps=[]):
    mapData = ast.literal_eval(requests.get("http://" + utils.ipAddress + "/map/" + mapName).text)
    if not tiles:
        _, tiles, Ps = utils.updateData(mapData)

    scale = 100
    camera = {"scale": scale,
              "ox": ((size[0] - scale) / 2),
              "oy": (size[1] / 2)}

    update_clouds(tiles, camera)

    if player:
        tileId = mapData["players"][tileId]["tileId"]
    else:
        tileId = str(tileId)

    if utils.vertical:
        centerPoint = (mapData["tiles"][tileId]["location"][0], mapData["tiles"][tileId]["location"][1])
        camera["ox"] = ((size[0] - camera["scale"]) / 2) - centerPoint[0] * camera["scale"]
        camera["oy"] = (size[1] / 2) - centerPoint[1] * camera["scale"] * 0.866
    else:
        centerPoint = (mapData["tiles"][tileId]["location"][1], mapData["tiles"][tileId]["location"][0])
        camera["oy"] = ((size[0] - camera["scale"]) / 2) - centerPoint[0] * camera["scale"] + 53 + ((53 * centerPoint[0]) / 4.0)
        if centerPoint[0] % 2 == 0:
            camera["ox"] = (size[1] / 2) - centerPoint[1] * camera["scale"] * 0.866 - 45 - ((40 * centerPoint[1]) / 3.0)
        else:
            camera["ox"] = (size[1] / 2) - centerPoint[1] * camera["scale"] * 0.866 - 5 - ((40 * centerPoint[1]) / 3.0)

    tiles = calculateWeather(tiles, camera, mapData["weather"]["seed"], mapData["weather"]["scroll"])

    pygame.init()

    utils.setFonts()

    flags = pygame.HIDDEN
    pygame.display.set_mode((0, 0), flags, vsync=1)
    surface = pygame.Surface(size)
    surface.fill(utils.colors["background"])

    if player:
        render_perspective(surface, tiles, Ps, camera, tileId)
    else:
        render_full_screen(surface, tiles, Ps, camera)

    pygame.image.save(surface, "map.png")


def calculateWeather(tiles, camera, seed, scroll):
    noise = PerlinNoise(octaves=2, seed=seed)
    for tile in tiles:
        x = tile.loc[0]
        y = tile.loc[1]

        if (y % 2) == 0:
            x = x + 0.5
        x = (x * camera["scale"])
        y = (y * camera["scale"] * 0.866)
        if not utils.vertical:
            x, y = y, x

        noiseForPixel = noise([(x / 1000) + scroll, (y / 1000) + scroll])
        tile.setWeather(noiseForPixel)
    return tiles


def update_clouds(tiles, camera):
    global cloudNodePoints

    random.seed(1)
    cloudNodePoints = []
    for r, t in rtpairs(25):
        cloudNodePoints.append(((r * np.cos(t)) + (offset * (random.random() - 0.5)), (r * np.sin(t)) + (offset * (random.random() - 0.5))))

    newCloudPoints = []
    for point in cloudNodePoints:
        x = (point[0] * (camera["scale"] + utils.cloudScale)) + camera["ox"]
        y = (point[1] * (camera["scale"] + utils.cloudScale) * 0.866) + camera["oy"]
        x, y = y, x

        minTileId = None
        minTileDistance = 10000000
        for tile in tiles:
            tx = tile.loc[0]
            ty = tile.loc[1]
            if (ty % 2) == 0:
                tx = tx + 0.5
            tx = (tx * camera["scale"]) + camera["ox"]
            ty = (ty * camera["scale"] * 0.866) + camera["oy"]
            if not utils.vertical:
                tx, ty = ty, tx

            dist = distanceBetweenTwoPoints((x, y), (tx, ty))
            if dist < minTileDistance:
                minTileId = tile.id
                minTileDistance = dist

        if minTileDistance <= camera["scale"] / 2:
            newCloudPoints.append((point[0], point[1], minTileId))

    cloudNodePoints = newCloudPoints

    for tile in tiles:
        tile.cloudPoints = []
    for point in cloudNodePoints:
        for tile in tiles:
            if tile.id == point[2]:
                tile.cloudPoints.append((point[0], point[1]))


def get_map_image_by_player(mapName, playerName, size):
    update_player_vision(mapName, playerName)

    mapData = ast.literal_eval(requests.get("http://" + utils.ipAddress + "/map/" + mapName).text)
    _, Ms, Ps = utils.updateData(mapData)

    for tile in Ms:
        if str(tile.id) in mapData["players"][playerName]["rememberedTiles"]:
            tile.remembered = True
            tile.rType = mapData["players"][playerName]["rememberedTiles"][tile.id]["type"]
            tile.rLabel = mapData["players"][playerName]["rememberedTiles"][tile.id]["label"]
        else:
            tile.remembered = False

    get_map_image_by_tile(mapName, playerName, size, True, Ms, Ps)


def update_player_vision(mapName, playerName):
    mapData = ast.literal_eval(requests.get("http://" + utils.ipAddress + "/map/" + mapName).text)
    _, Ms, Ps = utils.updateData(mapData)

    centerId = mapData["players"][playerName]["tileId"]
    _, newVisibleTiles = calculate_vision(Ms, centerId)

    for tile in newVisibleTiles:
        if tile.label == "":
            requests.put("http://" + utils.ipAddress + "/map/" + mapName + "/players/" + playerName + "/remember/" + str(tile.id) + "/" + str(tile.type) + "/_")
        else:
            requests.put("http://" + utils.ipAddress + "/map/" + mapName + "/players/" + playerName + "/remember/" + str(tile.id) + "/" + str(tile.type) + "/" + str(tile.label))
