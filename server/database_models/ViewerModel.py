# from database_models import conn, cur
import json
from server import app
cur = app.db.cur
conn = app.db.conn

class ViewerModel:
    def __init__(self, user, room_id):
        self.user = user
        self.room_id = room_id

    @staticmethod
    def make_new_viewer(user, room):
        '''Делает нового наблюдателя для комнаты room из пользователя user'''
        cur.execute('''INSERT INTO viewers 
            (user_id, room_id) VALUES (%s, %s)''',
            (user.id, room.id))
        conn.commit()
        return ViewerModel(user, room.id)
    def leave_room(self):
        '''Дописывает в поле time_left время, когда он покинул комнату'''
        cur.execute('''UPDATE viewers 
                time_left=NOW()::TIMESTAMP 
                WHERE user_id=%s AND room_id=%s''', 
                (self.user.id, self.room_id))
        conn.commit()
    
    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def __json__(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)