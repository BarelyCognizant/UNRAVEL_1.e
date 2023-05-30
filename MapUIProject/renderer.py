import ast

import pygame
import requests

import utils


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
                    if tile.visible:
                        tile.render(surface, camera, currentFocusTile == tile)
    for i in range(lowestX, highestX + 1):
        for tile in tiles:
            if tile.loc[0] == i:
                playersInLocation = []
                for player in players:
                    if player.loc == tile.id:
                        playersInLocation.append(player)
                for j in reversed(range(len(playersInLocation))):
                    playersInLocation[j].render(surface, camera, tiles, j + 1)
    for i in range(lowestX, highestX + 1):
        for tile in tiles:
            if tile.loc[0] == i:
                if tile.visible:
                    tile.renderLabels(surface, camera)


def render_full_screen(surface, tiles, players, camera, placementMode=False, currentFocusTile=None):
    for tile in tiles:
        tile.visible = True
    render_screen(surface, tiles, players, camera, placementMode, currentFocusTile)


def render_perspective(surface, tiles, players, camera, centerId):
    centerTile = None
    for tile in tiles:
        tile.visible = False
        tile.distance = -1
        if tile.id == centerId:
            tile.visible = True
            tile.distance = 0
            centerTile = tile
    visionDistance = 2
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

    render_screen(surface, tiles, players, camera)


def get_map_image_by_tile(mapName, tileId, size, player=False):
    mapData = ast.literal_eval(requests.get("http://" + utils.ipAddress + "/map/" + mapName).text)
    _, Ms, Ps = utils.updateData(mapData)

    scale = 100
    camera = {"scale": scale,
              "ox": ((size[0] - scale) / 2),
              "oy": (size[1] / 2)}

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

    pygame.init()

    utils.setFonts()

    surface = pygame.Surface(size)
    surface.fill(utils.colors["background"])

    if player:
        render_perspective(surface, Ms, Ps, camera, tileId)
    else:
        render_full_screen(surface, Ms, Ps, camera)

    pygame.image.save(surface, "map.png")


def get_map_image_by_player(mapName, playerName, size):
    get_map_image_by_tile(mapName, playerName, size, True)