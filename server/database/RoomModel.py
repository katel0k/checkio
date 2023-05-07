from psycopg2 import sql
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
            self._game_manager.white_player = user
        elif gm.black_player is None:
            self._game_manager.black_player = user

    def unset_player(self, user):
        gm = self._game_manager
        if gm.white_player == user:
            (gm.white_player, gm.black_player) = (gm.black_player, None)
        elif gm.black_player == user:
            gm.black_player = None

    def change_setting(self, **settings):
        '''Возможные настройки: пока никаких:)'''
        pass

    def is_ready_to_start(self):
        gm = self._game_manager
        return gm.white_player is not None and gm.black_player is not None

class GameManagerPlayingState:
    def __init__(self, game_manager):
        self._game_manager = game_manager

        gm = self._game_manager
        self._game_model = GameModel.make_new_game(gm._room.id, gm.white_player, gm.black_player)
        # self._game = Game()

    def unset_player(self, user):
        pass

    def handle_move(self, move):
        return self._game_model.handle_move(move)
        # return self._game.handle_move(move)

    def get_outcome(self):
        return self._game.outcome
    def get_game(self):
        game = self._game_model.game
        return {
            'field': game.field,
            'is_white_move': game.is_white_move,
            'outcome': game.outcome,
            'id': self._game_model.id
        }

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
    
    def set_player(self, user):
        '''Устанавливает user как одного из игроков'''
        self._state.set_player(user)

    def unset_player(self, user):
        self._state.unset_player(user)

    def change_setting(self, **settings):
        '''Возможные настройки: пока никаких:)'''
        self._state.change_setting(**settings)

    def is_player_set(self, user):
        return self.white_player == user or self.black_player == user

    def is_ready_to_start(self):
        return self._state.is_ready_to_start()
    def start_game(self):
        # if not self.is_ready_to_start(): return
        self._state = GameManagerPlayingState(self)
    def handle_move(self, move):
        return self._state.handle_move(move)
    def get_outcome(self):
        return self._state.get_outcome()
    def get_game(self):
        return self._state.get_game()
    def finish_game(self):
        self._black_player = None
        self._state = GameManagerSetupState()


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



WAITING = 'waiting'
PLAYING = 'playing'
DEAD = 'dead'


class RoomModel:
    def __init__(self, id, **kwargs):
        self.id = id
        self._state = kwargs.get('state', WAITING)
        self._viewer_manager = ViewerManager(self)
        self._game_manager = GameManager(self)
        self._game_setter = None

    @property
    def white_player(self):
        return self._game_manager._white_player
    @property
    def black_player(self):
        return self._game_manager._black_player

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
        self.__update_field('state', value.upper())
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
        self._game_manager.set_player(user)
    def is_player_set(self, user):
        return self._game_manager.is_player_set(user)
    def is_ready_to_start(self):
        return self._game_manager.is_ready_to_start()
    def start_game(self):
        self._game_manager.start_game()
        self.state = PLAYING
    def handle_move(self, move):
        return self._game_manager.handle_move(move)
    def get_outcome(self):
        return self._game_manager.get_outcome()
    def get_game(self):
        return self._game_manager.get_game()
    def finish_game(self):
        self._game_manager.finish_game()
        self.state = WAITING


'''
класс комнаты обрабатывает собственное состояние включая события в комнате
room.handle(event_name, *args)



'''

__all__ = ['RoomModel']