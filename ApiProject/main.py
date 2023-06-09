from fastapi import FastAPI
import json
import uuid
import os

app = FastAPI()


@app.post("/map/{mapName}", status_code=201)
async def create_map_object(mapName: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        return {"message": "Map already exists."}
    newMapData = {
        "hash": str(uuid.uuid4()),
        "name": mapName,
        "weather": {
            "seed": 1,
            "scroll": 0
        },
        "idCount": 1,
        "tiles": {
            0: {
                "location": (0, 0),
                "type": "grass\\forest.png",
                "label": "",
                "description": "",
                "comments": ""
            }
        },
        "players": {},
        "npcs": {}
    }
    with open("maps/" + mapName + ".json", "x") as outfile:
        json.dump(newMapData, outfile)
    return newMapData


@app.get("/map/{mapName}", status_code=200)
async def get_map_object(mapName: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        return mapData
    return {"message": "Map does not exist."}


@app.delete("/map/{mapName}", status_code=200)
async def delete_map_object(mapName: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        os.remove("maps/" + mapName + ".json")
        return {"message": "Map was deleted."}
    else:
        return {"message": "Map does not exist."}


@app.post("/map/{mapName}/tile/{x}/{y}/{type}/{id}/{hash}", status_code=201)
async def create_tile(mapName: str, x: int, y:int, type: str, id: int, hash: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if mapData["hash"] == hash:
            for tile in mapData["tiles"]:
                if mapData["tiles"][tile]["location"][0] == x and mapData["tiles"][tile]["location"][1] == y:
                    return {"message": "This tile already exists."}
            mapData["hash"] = str(uuid.uuid4())
            mapData["idCount"] += 1
            mapData["tiles"][id] = {"location": [x, y], "type": type.replace("_", "\\"), "label": "", "description": "", "comments": ""}
            os.remove("maps/" + mapName + ".json")
            with open("maps/" + mapName + ".json", "x") as outfile:
                json.dump(mapData, outfile)
            return mapData
        else:
            return {"message": "Map has change since your last pull. Sync and request again."}
    return {"message": "Map does not exist."}


@app.delete("/map/{mapName}/tile/{id}/{hash}", status_code=200)
async def delete_tile(mapName: str, id: str, hash: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if mapData["hash"] == hash:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"].pop(tile)
                    print(tile)
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
            return {"message": "This tile does not exist."}
        else:
            return {"message": "Map has change since your last pull. Sync and request again."}
    return {"message": "Map does not exist."}


@app.put("/map/{mapName}/tile/{type}/{id}/{hash}", status_code=200)
async def change_tile(mapName: str, type:str, id: str, hash: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if mapData["hash"] == hash:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["type"] = type.replace("_", "\\")
                    print(tile)
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
            return {"message": "This tile does not exist."}
        else:
            return {"message": "Map has change since your last pull. Sync and request again."}
    return {"message": "Map does not exist."}


@app.post("/map/{mapName}/label/{id}/{label}", status_code=201)
async def write_label(mapName: str, id: str, label: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["label"] = label
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.delete("/map/{mapName}/label/{id}", status_code=201)
async def delete_label(mapName: str, id: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["label"] = ""
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.post("/map/{mapName}/description/{id}/{description}", status_code=201)
async def write_description(mapName: str, id: str, description: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["description"] = description
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.delete("/map/{mapName}/description/{id}", status_code=201)
async def delete_description(mapName: str, id: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["description"] = ""
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.post("/map/{mapName}/comments/{id}/{comments}", status_code=201)
async def write_comments(mapName: str, id: str, comments: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["comments"] = comments
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.put("/map/{mapName}/comments/{id}/{comments}", status_code=201)
async def append_comments(mapName: str, id: str, comments: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["comments"] = mapData["tiles"][tile]["comments"] + comments
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.delete("/map/{mapName}/comments/{id}", status_code=201)
async def delete_comments(mapName: str, id: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    mapData["hash"] = str(uuid.uuid4())
                    mapData["tiles"][tile]["comments"] = ""
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.post("/map/{mapName}/players/{name}/{id}/{r}/{g}/{b}/{npc}", status_code=201)
async def create_player(mapName: str, name: str, id: str, r: int, g: int, b: int, npc: bool):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            for tile in mapData["tiles"]:
                if tile == id:
                    listIndex = "players"
                    if npc:
                        listIndex = "npcs"
                    mapData["hash"] = str(uuid.uuid4())
                    mapData[listIndex][name] = {
                        "tileId": id,
                        "color": [r, g, b],
                        "rememberedTiles": {}
                    }
                    os.remove("maps/" + mapName + ".json")
                    with open("maps/" + mapName + ".json", "x") as outfile:
                        json.dump(mapData, outfile)
                    return mapData
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.put("/map/{mapName}/players/{name}/{id}", status_code=200)
async def move_player(mapName: str, name: str, id: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            if name in mapData["players"]:
                for player in mapData["players"]:
                    if player == name:
                        mapData["hash"] = str(uuid.uuid4())
                        mapData["players"][name]["tileId"] = id
                        os.remove("maps/" + mapName + ".json")
                        with open("maps/" + mapName + ".json", "x") as outfile:
                            json.dump(mapData, outfile)
                        return mapData
            else:
                return {"message": "Player does not exist."}
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}


@app.put("/map/{mapName}/players/{name}/remember/{id}/{type}/{label}", status_code=200)
async def upgrade_players_remembered_tiles(mapName: str, name: str, id: str, type: str, label: str):
    if os.path.isfile("maps/" + mapName + ".json"):
        with open("maps/" + mapName + ".json") as mapJsonFile:
            mapData = json.load(mapJsonFile)
        if id in mapData["tiles"]:
            if name in mapData["players"]:
                for player in mapData["players"]:
                    if player == name:
                        mapData["hash"] = str(uuid.uuid4())
                        mapData["players"][name]["rememberedTiles"][id] = {"type": type, "label": label.replace("_", "")}
                        os.remove("maps/" + mapName + ".json")
                        with open("maps/" + mapName + ".json", "x") as outfile:
                            json.dump(mapData, outfile)
                        return mapData
            else:
                return {"message": "Player does not exist."}
        else:
            return {"message": "Tile does not exist."}
    return {"message": "Map does not exist."}
