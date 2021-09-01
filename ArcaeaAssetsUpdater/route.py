"""
 - Author: DiheChen
 - Date: 2021-08-15 00:13:33
 - LastEditTime: 2021-09-01 21:39:36
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import listdir, path
from urllib.parse import urljoin
from urllib.request import pathname2url

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
import ujson as json

from config import Config
from assets_updater import ArcaeaAssetsUpdater

app = FastAPI()
songs_dir = path.abspath(
    path.join(path.dirname(__file__), "data", "assets", "songs"))
char_dir = path.abspath(
    path.join(path.dirname(__file__), "data", "assets", "char"))


@app.get("/assets/songs/{song_id}/{file_name}")
async def _(song_id: str, file_name: str):
    if not path.exists(path.join(songs_dir, song_id)) and ("dl_" + song_id in listdir(songs_dir)):
        song_id = "".join(["dl_", song_id])
    return FileResponse(path.join(songs_dir, song_id, file_name))


@app.get("/api/version")
async def _(request: Request):
    with open(path.join(path.dirname(__file__), "data", f"version.json"), "r") as file:
        return json.loads(file.read())


@app.get("/api/song_list")
async def _(request: Request):
    song_dict = dict()
    for song in listdir(songs_dir):
        if path.isdir(path.join(songs_dir, song)):
            if path.exists(path.join(songs_dir, song, "base.jpg")):
                song_dict[song.replace("dl_", "")] = [urljoin(str(request.base_url), pathname2url(
                    path.join("assets", "songs", song.replace("dl_", ""), "base.jpg")))]
                if path.exists(path.join(songs_dir, song, "3.jpg")):
                    song_dict[song.replace("dl_", "")].append(urljoin(str(request.base_url), pathname2url(
                        path.join("assets", "songs", song.replace("dl_", ""), "3.jpg"))))
    return song_dict


@app.get("/assets/char/{image_name}")
async def _(image_name: str):
    return FileResponse(path.join(songs_dir, char_dir, image_name))


@app.post("/api/force_update")
async def _(request: Request, background_tasks: BackgroundTasks):
    if "Authorization" in request.headers and request.headers["Authorization"] == Config.token:
        background_tasks.add_task(ArcaeaAssetsUpdater.force_update)
        return {"message": "Succeeded."}
    else:
        return {"message": "Access denied."}
