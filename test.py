from ArcaeaAssetsUpdater.song_info.database import charts, Data



def song_random(
    start: float, end: float, difficulty: int = 0, withsonginfo: bool = True
):
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


# res = asyncio.run(song_random(10, 11, 2))
# print(res)
res = song_random(11, 11, 2)
print(res)
