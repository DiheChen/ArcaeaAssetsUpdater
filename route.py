"""
 - Author: DiheChen
 - Date: 2021-08-15 00:13:33
 - LastEditTime: 2021-08-15 04:54:58
 - LastEditors: DiheChen
 - Description: None
 - GitHub: https://github.com/Chendihe4975
"""
from os import listdir, path
from urllib.parse import urljoin
from urllib.request import pathname2url

from fastapi import FastAPI
from fastapi.responses import FileResponse
from config import Config

app = FastAPI()
songs_dir = path.abspath(
    path.join(path.dirname(__file__), "data", "assets", "songs"))


@app.get("/assets/songs/{song_id}/{file_name}")
async def _(song_id: str, file_name: str):
    if not path.exists(path.join(songs_dir, song_id)) and ("dl_" + song_id in listdir(songs_dir)):
        song_id = "".join(["dl_", song_id])
    return FileResponse(path.join(songs_dir, song_id, file_name))


@app.get("/api/song_list")
async def _():
    song_dict = dict()
    for song in listdir(songs_dir):
        if path.isdir(path.join(songs_dir, song)):
            song_dict[song.replace("dl_", "")] = urljoin(
                Config.url, pathname2url(path.join("assets", "songs", song.replace("dl_", ""), "base.jpg")))
    return song_dict
