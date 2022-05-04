from .database import alias, charts, Data


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