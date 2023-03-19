from flask_login import UserMixin
from setup_db import cur, conn
from enum import Enum

from server import login_manager

class User(UserMixin):
    def __init__(self, email, password_hash, username):
        super()
        self.email = email
        self.password_hash = password_hash
        self.username = username

    def make_new_db_record(self):
        cur.execute('''INSERT INTO users 
            (email, password_hash, username) 
            VALUES (%s, %s, %s)''',
            (self.email,
            self.password_hash,
            self.username)
        )
        # TODO: get user id here
        conn.commit()

    @login_manager.user_loader # doesn't seem to be a correct decision
    def load_user(self):
        pass # TODO:

    # @staticmethod
    # def make_new_user():


    def get_id(self):
        return self.email # TODO: temporary

    # def get_from_DB(db_tuple):
    #     u = User(db_tuple[1]) # TODO: omg wtf
    #     return u
    def __repr__(self):
        return self.__str__()

class Player:
    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id
        self.is_white = True

    def make_new_db_record(self):
        cur.execute('''
            INSERT INTO players
            (user_id, game_id, is_white) VALUES
            (%s, %s, %s)
        ''', (
            self.user_id, self.game_id, self.is_white
        ))
        conn.commit()

    @staticmethod
    def get_from_db_record(user_id, game_id, is_white):
        pass # TODO: make SELECT query to accomodate this request

    def assign_color(self, color):
        self.is_white = color
    
    def __str__(self):
        return ('<Player user_id: %s, game_id: %s, is_white: %s>' %
                (self.user_id, self.game_id, self.is_white))
    
    def __repr__(self):
        return self.__str__()
    
class GameMove:
    def __init__(self):
        pass
    def __repr__(self):
        return self.__str__()

class Game:
    def __init__(self):
        self.order_color = True
        self.field = list(map(lambda s:
            [GameCell(x) for x in s],
                ['0b0b0b0b', 'b0b0b0b0', '0b0b0b0b', '00000000',
                '00000000', 'w0w0w0w0', '0w0w0w0w', 'w0w0w0w0'])) # i'm just lazy:)
        # self.move_history = []
    def make_move(self, move):
        pass
    # pass
    def __repr__(self):
        return self.__str__()

class RoomState(Enum):
    WAITING = 0
    PLAYING = 1
    DEAD = 2

class Room:
    ''' Этот класс соответствует записям в таблице rooms в базе данных.
    Он также используется для хранения комнат во время работы сервера. 
    Потому у него есть поля player_white, player_black: Player
    '''
    def __init__(self, 
                 player_white: bool = None, 
                 player_black: bool = None,
                 state: RoomState = RoomState.WAITING,
                 game: Game = None):
        self.player_white = None # для удобства и быстрого доступа
        self.player_black = None

        self.state = RoomState.WAITING
        self.game = None

    def make_new_db_record(self):
        '''Создает запись, соответсвующую объекту, в базе данных'''
        cur.execute('''INSERT INTO rooms 
            () VALUES ()''')
        conn.commit()

    @staticmethod
    def get_from_db_record(id: int):
        '''Создает комнату из '''
        cur.execute('''''') # TODO: сделать запрос, получающий полную комнату
        # conn.getchone()


    def set_player(self, player: Player):
        '''Устанавливает игрока в свободный цвет и автоматически назначает этот цвет игроку'''
        if self.player_white is None:
            self.player_white = player
            player.set_color(True)
        elif self.player_black is None:
            self.player_balck = player
            player.set_color(False)

    def is_ready_to_start(self):
        '''Возвращает True, если комната готова для начала игры'''
        return self.player_white is None or self.player_black is None

    def start_game(self):
        '''Пытается начать новую игру
        Если хотя бы один из игроков не установлен или произошла другая ошибка, возвращает False
        Иначе возвращает True'''
        if not self.is_ready_to_start():
            return False

        self.game = Game()

        return True


    def __str__(self):
        return ('<Room white: %s, black: %s, state: %s, game: %s>' %
                self.player_white, self.player_black, self.state, self.game)





class ActivePlayer:
    def __init__(self):
        pass
    def __repr__(self):
        return self.__str__()