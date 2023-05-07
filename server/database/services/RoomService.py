from server import app

from ..models import RoomModel, UserModel, ViewerModel

conn = app.db.conn
cur = app.db.cur

def make_room(room_tuple: tuple | None) -> RoomModel | None:
    if room_tuple is None: return None
    return RoomModel(
        id=room_tuple[0],
        state=room_tuple[1],
        created_dttm=room_tuple[2]
    )

def get_room(id: int) -> RoomModel | None:
    cur.execute('''SELECT id, state, created_dttm FROM rooms WHERE id=%s''', (id, ))
    room_tuple = cur.fetchone()
    return make_room(room_tuple)

def make_new_room() -> RoomModel | None:
    cur.execute('''INSERT INTO rooms DEFAULT VALUES
        RETURNING id, state, created_dttm''')
    room_tuple = cur.fetchone()
    return make_room(room_tuple)

def join_user(room: RoomModel, user: UserModel) -> ViewerModel:
    cur.execute('''INSERT INTO viewers 
        (user_id, room_id) VALUES (%s, %s)
        RETURNING user_id, room_id, joined_dttm, left_dttm''',
        (room.id, user.id))
    viewer_tuple = cur.fetchone()
    return ViewerModel(
        user_id = viewer_tuple[0],
        room_id = viewer_tuple[1],
        joined_dttm = viewer_tuple[2],
        left_dttm = viewer_tuple[3]
    )

def leave_user(room: RoomModel, user: UserModel) -> None:
    cur.execute('''UPDATE viewers 
        time_left=NOW()::TIMESTAMP 
        WHERE user_id=%s AND room_id=%s''', 
        (user.id, room.id))
    conn.commit()

__all__ = ['get_room', 'make_new_room', 'join_user']