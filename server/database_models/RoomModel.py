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

GAME_MANAGER_SETUP_STATE = 'setup'
GAME_MANAGER_PLAYING_STATE = 'playing'

class GameManagerSetupState:
    def __init__(self, game_manager):
        self._game_manager = game_manager

    def set_player(self, user):
        gm = self._game_manager
        if gm.white_player == user or gm.black_player == user: return
        if gm.white_player is None:
            gm.white_player = user
        elif gm.black_player is None:
            gm.black_player = user

    def unset_player(self, user):
        gm = self._game_manager
        if gm.white_player == user:
            (gm.white_player, gm.black_player) = (gm.black_player, None)
        elif gm.black_player == user:
            gm.black_player = None

    def change_setting(self, **settings):
        '''Возможные настройки: пока никаких:)'''
        pass

    def is_game_ready(self):
        gm = self._game_manager
        return gm.white_player is not None and gm.black_player is not None

class GameManagerPlayingState:
    def __init__(self, game_manager):
        self._game_manager = game_manager

        gm = self._game_manager
        self._game = GameModel.make_new_game(gm._room.id, gm.white_player, gm.black_player)

    def unset_player(self, user):
        pass

    def handle_move(self, move):
        pass

    def get_outcome(self):
        pass    

class GameManager:
    '''Вспомогательный класс для класса RoomModel. Менеджит игру в комнату
    Умеет настраивать игру (устанавливать обоих игроков, менять ее настройки, удалять игроков во время настройки)
    Умеет определять, готова ли игра для начала
    Умеет проводить игру (начинать ее, делать ходы в игре, сообщать о победе/поражении)'''
    def __init__(self, room, **kwargs):
        self._room = room
        self._state = (GameManagerSetupState(self) 
                       if kwargs.get('state', GAME_MANAGER_SETUP_STATE) == GAME_MANAGER_SETUP_STATE
                        else GameManagerPlayingState(self))
        # состояния взаимодействуют с этими полями
        self._white_player = None
        self._black_player = None
    
    # это существует для того чтобы извне код не сломался
    @property
    def white_player(self):
        return self._white_player
    @white_player.setter
    def white_player(self, value):
        self._white_player = value
    @property
    def black_player(self):
        return self._black_player
    @black_player.setter
    def black_player(self, value):
        self._black_player = value
    
# TODO: понадобится переименовать по-человечески
    def set_player(self, user):
        '''Устанавливает user как одного из игроков'''
        self._state.set_player(user)

    def unset_player(self, user):
        self._state.unset_player(user)

    def change_setting(self, **settings):
        '''Возможные настройки: пока никаких:)'''
        self._state.change_setting(**settings)

# TODO: анаолгично, возможно, это бред
    def is_game_ready(self):
        return self._state.is_game_ready()
# TODO: возможно, это бред
    def start_game(self):
        if not self.is_game_ready(): return
        self._state = GameManagerPlayingState(self)

class GameSetter:
    def __init__(self, room):
        self._room = room
        

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


# TODO: подумать, добавить ли сюда обработку активного игрока, а то сейчас это делается в рутах
class ViewerManager:
    '''Вспомогательный класс для класса RoomModel. Менеджит всех людей в комнате(наблюдателей)
    Эти люди точно будут получать уведомления, о том, что происходит в комнате и о них должны быть записи в БД'''
    def __init__(self, room, **kwargs):
        '''Конструктор может получить на вход viewers - словарь пользователей, если комната подгружается из БД'''
        self._viewers = kwargs.get('viewers', dict())
        self._room = room

    def has_user(self, user):
        return user.id in self.viewers
    
    def connect_user(self, user):
        if self.has_user(user): return
        self.viewers[user.id] = ViewerModel.make_new_viewer(user, self._room)
        
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
        self._viewer_manager = ViewerManager(self)
        self._game_manager = GameManager(self)
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
        cur.execute('''INSERT INTO rooms DEFAULT VALUES RETURNING id''')
        conn.commit()
        res = cur.fetchone() 
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
            self._game_setter = GameSetter(self.id, user)
        else:
            self._game_setter.join_user(user)
    
    def is_ready_to_start(self):
        return self._game_setter is not None and self._game_setter.is_ready()
    
    def start_game(self):
        self._game_setter.start_game()

__all__ = ['RoomModel']