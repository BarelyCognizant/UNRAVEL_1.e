import ast
import requests

import sys

sys.path.append('..\\MapUIProject')
import renderer


# Online Python - IDE, Editor, Compiler, Interpreter

class Map:
    def __init__(self, ip_address="https://b112-2a0e-cb01-2d-2e00-18c7-6c1f-9246-110d.ngrok-free.app", name="Terra"):
        self.ipAddress = ip_address
        self.mapName = name
        self.mapData = ast.literal_eval(requests.get(self.ipAddress + "/map/"+self.mapName).text)


    def updateMap(self):
        self.mapData = ast.literal_eval(requests.get(self.ipAddress + "/map/"+self.mapName).text)  # 192.168.1.22

    def move(self, X, Y, player):

        exists, location = self.getLocationID(X, Y)
        if not exists:
            return "Location does not exist yet!"
        self.setPlayerLocation(X, Y, player)
        renderer.update_player_vision(self.mapName, player)
        return "Player successfully moved"

    #    def StealthRolls (Player, X,Y):
    #        players = getPlayersAtLocation (X,Y)

    def getPlayerLocation(self, player):
        return self.mapData["tiles"][self.mapData["players"][player]["tileId"]]["location"]

    def getAllPlayers(self):
        return self.mapData["players"]

    def getPlayersAtLocation(self, tile):
        players = []
        AllPlayers = self.getAllPlayers()
        for player in AllPlayers:
            if AllPlayers[player]["tileId"] == str(tile):
                players.append(player)

        return players

    def getLocationID(self, X, Y):
        for tile in self.mapData["tiles"]:
            if self.mapData["tiles"][tile]["location"][0] == X and self.mapData["tiles"][tile]["location"][1] == Y:
                return True, tile

        return False, None

    # sends off move command to the system
    def setPlayerLocation(self, X, Y, Player):
        ast.literal_eval(requests.put(
            self.ipAddress + "/map/"+self.name+"/players/" + str(Player) + "/" + str(self.getLocationID(X, Y)[1])).text)

    # The bot commands for Thomas

    # botMove is not properly implemented in terms of validation
    def botMove(self, tileID, Player):
        self.updateMap()
        r = ast.literal_eval(requests.put(
            self.ipAddress + "/map/"+self.name+"/players/" + str(Player) + "/" + str(tileID)).text)
        return r["message"] if "message" in r else "Player successfully moved"

    def N(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        return self.move(X - 1, Y, Player)

    def S(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        return self.move(X + 1, Y, Player)

    # Maxime has cursed these co-ordinates
    def NW(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        if (Y % 2 == 0):
            return self.move(X, Y - 1, Player)
        else:
            return self.move(X - 1, Y - 1, Player)

    def SW(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        if (Y % 2 != 0):
            return self.move(X, Y - 1, Player)
        else:
            return self.move(X + 1, Y - 1, Player)

    def NE(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        if (Y % 2 == 0):
            return self.move(X, Y + 1, Player)
        else:
            return self.move(X - 1, Y + 1, Player)

    def SE(self, Player):
        self.updateMap()
        X, Y = self.getPlayerLocation(Player)
        if (Y % 2 != 0):
            return self.move(X, Y + 1, Player)
        else:
            return self.move(X + 1, Y + 1, Player)

    def move_direction(self, player, direction):
        if direction == "N":
            return self.N(player)
        elif direction == "NW":
            return self.NW(player)
        elif direction == "NE":
            return self.NE(player)
        elif direction == "S":
            return self.S(player)
        elif direction == "SW":
            return self.SW(player)
        elif direction == "SE":
            return self.SE(player)
        else:
            return "Impossible direction provided. Valid directions: NW, N, NE, SE, S, SW"

    def set_label(self, tile_id, label):
        r = ast.literal_eval(requests.post(
            self.ipAddress + "/map/"+self.name+"/label/" + tile_id + "/" + label).text)
        return r["message"] if "message" in r else "Label successfully set"

    def delete_label(self, tile_id, label):
        r = ast.literal_eval(requests.post(
            self.ipAddress + "/map/"+self.name+"/label/" + tile_id).text)
        return r["message"] if "message" in r else "Label successfully deleted"

    def set_comments(self, tile_id, comments):
        r = ast.literal_eval(requests.post(
            self.ipAddress + "/map/"+self.name+"/comments/" + tile_id + "/" + comments).text)
        return r["message"] if "message" in r else "Comment successfully set"

    def delete_comments(self, tile_id):
        r = ast.literal_eval(requests.post(
            self.ipAddress + "/map/"+self.name+"/comments/" + tile_id).text)
        return r["message"] if "message" in r else "Comment successfully deleted"

    def append_comments(self, tile_id, comments):
        r = ast.literal_eval(requests.put(
            self.ipAddress + "/map/"+self.name+"/comments/" + tile_id + "/" + comments).text)
        return r["message"] if "message" in r else "Comment successfully updated"

    def add_player(self, tile_id, name, color):
        r = ast.literal_eval(requests.post(
            self.ipAddress + "/map/"+self.name+"/players/" + name + "/" + tile_id + "/" + color).text)
        return r["message"] if "message" in r else "Player successfully added"


# Valid Colors Hardcoded from the Map UI
def is_valid_color(color):
    colors = {"red": (255, 0, 0),
              "orange": (255, 98, 0),
              "yellow": (255, 255, 0),
              "green": (0, 255, 0),
              "lightblue": (0, 255, 255),
              "blue": (0, 0, 255),
              "purple": (119, 0, 255),
              "pink": (255, 0, 255)}
    return color in colors
