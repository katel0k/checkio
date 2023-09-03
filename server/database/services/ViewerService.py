from server import app
from typing import List
from ..models import RoomModel, ViewerModel

conn = app.db.conn

def get_all_viewers(room: RoomModel) -> List[ViewerModel]:
    cur = conn.cursor()
    cur.execute('''
        SELECT user_id, room_id, joined_dttm, left_dttm
        FROM rooms JOIN viewers ON (rooms.id = viewers.room_id)
        WHERE left_dttm IS NULL AND room_id = %s
    ''', (room.id, ))
    return [
        ViewerModel(
            viewer_tuple[0],
            viewer_tuple[1],
            viewer_tuple[2],
            viewer_tuple[3]
        ) for viewer_tuple in cur.fetchall()
    ]

__all__ = ['get_all_viewers']