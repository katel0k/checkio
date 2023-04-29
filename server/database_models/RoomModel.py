# from database_models import conn, cur, GameModel, ViewerModel
from psycopg2 import sql
# from ..application import Application
# app = Application()
from .User import *
from .PlayerModel import *
from .GameModel import *
from .ViewerModel import *
from server import app


cur = app.db.cur
conn = app.db.conn

class GameManager:
    def __init__(self, room_id, user):
        # TODO: если расширять этот интерфейс для других игр, ему потребуется переработка
        # тогда можно будет сделать его более полным
        # также надо будет добавить сеттер/геттер для настроек игры
        self.room_id = room_id
        self.creator = user
        self.opponent = None
        self.game = None

    @staticmethod
    def create_game(user):
        # TODO: add game types
        return GameManager(user)
    
    def join_user(self, user):
        self.opponent = user

    def is_playing(self):
        return self.game is not None
    
    def is_ready(self):
        return self.opponent is not None and self.creator is not None

    def start_game(self):
        self.game = GameModel.make_new_game(self.room_id, self.creator, self.opponent)
        

class ViewerManager:
    '''Вспомогательный класс для класса RoomModel. Менеджит всех людей в комнате(наблюдателей)
    Эти люди точно будут получать уведомления, о том, что происходит в комнате и о них должны быть записи в БД'''
    def __init__(self, room, **kwargs):
        '''Конструктор может получить на вход viewers - словарь пользователей, если комната подгружается из БД'''
        self._viewers = kwargs.get('viewers', dict())
        self.room = room

    def has_user(self, user):
        return user.id in self.viewers
    
    def connect_user(self, user):
        if self.has_user(user): return
        self.viewers[user.id] = ViewerModel.make_new_viewer(user, self.room)
        
    def disconnect_user(self, user):
        if not user.id in self.viewers: return
        viewer = self.viewers[user.id]
        viewer.leave_room()
        self.viewers.pop(user.id)
    
    @property
    def viewers(self):
        return self._viewers



# class RoomState(Enum):
WAITING = 'waiting'
PLAYING = 'playing'
DEAD = 'dead'


# что этот класс должен уметь:

# менеджмент пользоваетелй:
#     - подключаются viewers
        # connect_user(user)
#     - отключаются viewers
        # disconnect_user(user)
# менеджмент игры:
# 
# менеджмент базы данных


class RoomModel:
    def __init__(self, id, **kwargs):
        self.id = id
        self._state = kwargs.get('state', WAITING)
        # self._viewers = kwargs.get('viewers', {})
        self._viewer_manager = ViewerManager(self)
        self._game_setter = None

    @staticmethod
    def get_from_database():
        cur.execute('''
            SELECT id, state, user_id
            FROM rooms JOIN viewers ON (rooms.id = viewers.room_id)
            WHERE state <> 'DEAD' AND left_dttm IS NULL
        ''')
        room_list = {}
        for (id, state, user_id) in cur.fetchall():
            if id not in room_list:
                room_list[id] = RoomModel(id, state=state, viewers=dict())
            room_list[id]._viewers[user_id] = ViewerModel(user_id, id)
        return room_list

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, value):
        self._state = value
        self.__update_field('state', value)
        # cur.execute() TODO: make here room_history insert

    def __update_field(self, field, value):
        cur.execute(
            sql.SQL('''
            UPDATE rooms
            SET {}=%s WHERE id=%s
        ''').format(sql.Identifier(field)), (value, self.id))
        conn.commit()

    @staticmethod
    def make_new_room():
        '''Создает новую пустую комнату'''
        cur.execute('''INSERT INTO rooms DEFAULT VALUES''')
        conn.commit()
        # TODO: TERRIBLE CODE
        cur.execute('''SELECT max(id) FROM rooms''')
        res = cur.fetchone() # TODO: проблемы с асинхронностью??
        return RoomModel(id=res[0])
    
    
    def connect_user(self, user):
        self._viewer_manager.connect_user(user)
    def disconnect_user(self, user):
        self._viewer_manager.disconnect_user(user)
    @property
    def viewers(self):
        return self._viewer_manager.viewers
    
    def set_player(self, user):
        if self._game_setter is None:
            self._game_setter = GameManager(self.id, user)
        else:
            self._game_setter.join_user(user)
    
    def is_ready_to_start(self):
        return self._game_setter is not None and self._game_setter.is_ready()
    
    def start_game(self):
        self._game_setter.start_game()

__all__ = ['RoomModel']