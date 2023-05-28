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
        "name": mapName
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
