from os import listdir, path
from urllib.parse import urljoin
from urllib.request import pathname2url
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse
import ujson as json
import peewee as pw

from config import Config
from assets_updater import ArcaeaAssetsUpdater

from pydantic import BaseModel

app = FastAPI()
songs_dir = path.abspath(
    path.join(path.dirname(__file__), "data", "assets", "songs"))
char_dir = path.abspath(
    path.join(path.dirname(__file__), "data", "assets", "char"))

class Base(BaseModel):
    class Config:
        extra = "ignore"

class SongInfo(Base):
    name_en: str
    name_jp: Optional[str]
    artist: str
    bpm: str
    bpm_base: int
    set: str
    set_friendly: str
    time: int
    side: int
    world_unlock: bool
    remote_download: bool
    bg: str
    date: datetime
    version: float
    difficulty: int
    rating: int
    note: int
    chart_designer: str
    jacket_designer: str
    jacket_override: bool
    audio_override: bool
class Song(Base):
    song_id: str
    difficulties: List[SongInfo]
    alias: Optional[List[str]]

class SongList(Base):
    songs: List[Song]

class Data:
    db = pw.SqliteDatabase(path.abspath(path.join(path.dirname(__file__), "data", "arcsong.db")))
    with open (path.abspath(path.join(path.dirname(__file__), "data", "arcsong.json")), "r", encoding="UTF-8") as f:
        jsons = json.loads(f.read())
        song_list = SongList(**jsons["content"])

class alias(pw.Model):
    sid = pw.IntegerField()
    alias = pw.CharField()

    class Meta:
        database = Data.db
        primary_key = pw.CompositeKey("sid", "alias")


class charts(pw.Model):
    song_id = pw.CharField()
    rating = pw.IntegerField()
    rating_class = pw.IntegerField()

    class Meta:
        database = Data.db
        primary_key = pw.CompositeKey("song_id", "rating", "rating_class")

def song_alias(song: str):
    song_alias = (
        alias.get_or_none(alias.alias == song)
        if alias.get_or_none(alias.alias == song)
        else alias.get_or_none(alias.sid == song)
    )
    if song_alias:
        return {"status": 0, "content": song_alias.sid}
    else:
        return {"status": -5, "message": "invalid songname or songid"}


def song_random(start: float, end: float, difficulty: int = 0):
    result = charts.select().where(
        (charts.rating >= start * 10)
        & (end * 10 >= charts.rating)
        & (charts.rating_class == difficulty)
    )
    return [single_song.make_json(i) for i in result]


class single_song:
    def get_song_info(song_id: str, difficulty: int):
        song_list = Data.song_list
        for i in song_list.songs:
            if i.song_id == song_id:
                return i.difficulties[difficulty].dict()

    def make_json(data: charts):
        song_id = data.song_id
        difficulty = data.rating_class
        song_info = single_song.get_song_info(song_id, difficulty)
        jsons = {
            "song_id": song_id,
            "difficulty": difficulty,
            "song_info": song_info,
        }
        return jsons



@app.get("/assets/songs/{song_id}/{file_name}")
async def _(song_id: str, file_name: str):
    if not path.exists(path.join(songs_dir, song_id)) and ("dl_" + song_id in listdir(songs_dir)):
        song_id = "".join(["dl_", song_id])
    return FileResponse(path.join(songs_dir, song_id, file_name))


@app.get("/api/version")
async def _(request: Request):
    with open(path.join(path.dirname(__file__), "data", "version.json"), "r") as file:
        return json.loads(file.read())


@app.get("/api/slst")
async def _(request: Request):
    return FileResponse(path.join(songs_dir, "songlist"))


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


@app.get("/api/char_list")
async def _(request: Request):
    char_list = dict()
    for char in listdir(char_dir):
        char_list[char] = urljoin(str(request.base_url), pathname2url(
                        path.join("assets", "char", char)))
    return char_list


@app.get("/assets/char/{image_name}")
async def _(image_name: str):
    return FileResponse(path.join(char_dir, image_name))


@app.get("/api/songrandom")
async def _(start: float, end: float, difficulty: int = 0):
    return song_random(start, end, difficulty)

@app.get("/api/songalias")
async def _(song: str):
    return song_alias(song)


@app.post("/api/force_update")
async def _(request: Request, background_tasks: BackgroundTasks):
    if "Authorization" in request.headers and request.headers["Authorization"] == Config.token:
        background_tasks.add_task(ArcaeaAssetsUpdater.force_update)
        return {"message": "Succeeded."}
    else:
        return {"message": "Access denied."}


@app.post("/api/unzip")
async def _(request: Request, background_tasks: BackgroundTasks):
    if "Authorization" in request.headers and request.headers["Authorization"] == Config.token:
        background_tasks.add_task(ArcaeaAssetsUpdater.unzip_file)
        return {"message": "Succeeded."}
    else:
        return {"message": "Access denied."}
