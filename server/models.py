from flask_login import UserMixin
from setup_db import cur, conn
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from sys import stderr
from server import login_manager
from psycopg2 import sql
import game_logic
import sys

class LoginError(Exception):
    '''Такая ошибка происходит при неудачной попытке входа в аккаунт'''
    def __init__(self, msg=None):
        super().__init__(msg)

class RegisterError(Exception):
    '''Такая ошибка происходит при неудачной попытке регистрации пользователя'''
    def __init__(self, msg=None):
        super().__init__(msg)

# TODO: separate into another file
# TODO: write database module for all transactions
class User(UserMixin):
    def __init__(self, **kwargs):
        super()
        self.id = kwargs['id']
        self._email = kwargs['email']
        self._password_hash = kwargs['password_hash']
        self._nickname = kwargs['nickname']
        self._rating = kwargs['rating']

    def __update_field(self, field, value):
        cur.execute(
            sql.SQL('''
            UPDATE users
            SET {}=%s WHERE id=%s
        ''').format(sql.Identifier(field)), (value, self.id))
        conn.commit()

    @property
    def password(self):
        return self._password_hash
    @password.setter
    def password(self, value):
        self._password_hash = generate_password_hash(value)
        self.__update_field('password_hash', self.password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
    
    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, value):
        self._email = value
        self.__update_field('email', self.email)

    @property
    def nickname(self):
        return self._nickname
    @nickname.setter
    def nickname(self, value):
        self._nickname = value
        self.__update_field('nickname', self.nickname)

    @property
    def rating(self):
        return self._rating
    @rating.setter
    def rating(self, value):
        self._rating = value
        self.__update_field('rating', self.rating)


    @staticmethod
    def register_new_user(email, password, nickname):
        '''Регистрирует нового пользователя в базе данных
            Выдает ValueError если пользователь уже был в базе данных
        '''
        if User.__fetch_user(email=email) is not None:
            raise RegisterError
        cur.execute(
            '''INSERT INTO users 
                (email, password_hash, nickname) 
                VALUES (%s, %s, %s)''',
            (email,
             generate_password_hash(password),
             nickname)
        )
        conn.commit()
        return User.__fetch_user(email=email)
    
    @staticmethod
    def __transform_db_output(info):
        '''Эта функция нужна для общности трансформации
            здесь проще будет менять структуру БД'''
        return {
            'id': info[0],
            'nickname': info[1],
            'email': info[2],
            'password_hash': info[3],
            'rating': info[4]
        }

    @staticmethod
    @login_manager.user_loader
    def load_user(id):
        '''Загружает пользователя из базы данных по его айдишнику, 
            нужно для плагина flask_login'''
        return User.__fetch_user(id=id)

    @staticmethod
    def login_user(email, password):
        '''Входит пользователем в аккаунт и возвращает объект пользователя
            Выдает ValueError если такой пользователь не существует или пароль неверный'''
        
        user = User.__fetch_user(email=email)
        if user is None:
            raise LoginError('Такой пользователь не найден')
        
        if not user.check_password(password):
            raise LoginError('Неправильный пароль')
        
        return user
    
    @staticmethod
    def __fetch_user(**kwargs):
        if 'id' in kwargs:
            cur.execute('''
                SELECT * FROM users WHERE id=%s
            ''', (kwargs['id'],))
        elif 'email' in kwargs:
            cur.execute('''
                SELECT * FROM users WHERE email=%s
            ''', (kwargs['email'],))
        res = cur.fetchone()
        return User(**User.__transform_db_output(res)) if res is not None else None

    def get_id(self):
        '''Нужно для плагина flask_login'''
        return self.id

    def __str__(self):
        return 'id: %s, email: %s, username: %s' % (self.id, self.email, self.username)
    def __repr__(self):
        return self.__str__()

class Viewer:
    def __init__(self, user_id, room_id):
        self.user_id = user_id
        self.room_id = room_id

    @staticmethod
    def make_new_viewer(user, room):
        '''Делает нового наблюдателя для комнаты room из пользователя user'''
        cur.execute('''INSERT INTO viewers 
            (user_id, room_id) VALUES (%s, %s)''',
            (user.id, room.id))
        conn.commit()
        return Viewer(user.id, room.id)
    def leave_room(self):
        '''Дописывает в поле time_left время, когда он покинул комнату'''
        cur.execute('''UPDATE viewers 
                time_left=NOW()::TIMESTAMP 
                WHERE user_id=%s AND room_id=%s''', 
                (self.user_id, self.room_id))
        conn.commit()


class Player:
    def __init__(self, user_id, game_id, is_white):
        self.user_id = user_id
        self.game_id = game_id
        self.is_white = is_white

    @staticmethod
    def make_new_player(user_id, game_id, is_white):
        cur.execute('''
            INSERT INTO user_games
            (user_id, game_id, is_white) VALUES
            (%s, %s, %s)
        ''', (
            user_id, game_id, is_white
        ))
        conn.commit()
        return Player(user_id, game_id, is_white)
    
# class GameMove:
#     def __init__(self):
#         pass
#     def __repr__(self):
#         return self.__str__()

class Game:
    def __init__(self, id, room_id):
        self.id = id
        self.room_id = room_id
        self.white_player = None
        self.black_player = None
        self.game = game_logic.Game()
    
    @staticmethod
    def make_new_game(room_id, white_user, black_user):
        cur.execute('''
            INSERT INTO games (room_id) VALUES (%s)
        ''', (room_id,))
        conn.commit()
        # TODO: TERRIBLE CODE
        cur.execute('''
            SELECT max(id) FROM games WHERE room_id=%s
        ''', (room_id,))
        res = cur.fetchone()
        game = Game(res[0], room_id)
        game.white_player = Player.make_new_player(white_user, game.id, True)
        game.black_player = Player.make_new_player(black_user, game.id, False)
        return game

    def handle_move(self, move):
        print('made move', file=sys.stderr)
        res = self.game.handle_move(move)
        if not res: return move
        cur.execute('''
            INSERT INTO turns (game_id, index, user_id, body)
            VALUES (%s, %s, %s, %s)
        ''', (self.id, 0, 
              self.white_player.user_id if move.is_white_player else self.black_player.user_id,
              str(move)))
        conn.commit()
        return move
        # GameMove(move.field_from, move.field_to, move.playerColor)


class GameSetter:
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
        return GameSetter(user)
    
    def join_user(self, user):
        self.opponent = user

    def is_playing(self):
        return self.game is not None
    
    def is_ready(self):
        return self.opponent is not None and self.creator is not None

    def start_game(self):
        self.game = Game.make_new_game(self.room_id, self.creator, self.opponent)
        

# class RoomState(Enum):
WAITING = 'waiting'
PLAYING = 'playing'
DEAD = 'dead'

class Room:
    def __init__(self, id):
        self.id = id
        self._state = WAITING
        self._viewers = {}
        self._game_setter = None

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
        return Room(id=res[0])
    
    
    def has_viewer(self, user):
        return user.id in self._viewers
    
    def add_viewer(self, user):
        if self.has_viewer(user):
            return # TODO: добавить сообщение об ошибке?
        viewer = Viewer.make_new_viewer(user, self)
        self._viewers[viewer.user_id] = viewer
        
    def remove_viewer(self, viewer):
        if not self.has_viewer(viewer):
            return # TODO: добавить сообщение об ошибке?
        viewer.leave_room()
        self._viewers.pop(viewer.id)
    
    def set_player(self, user):
        if self._game_setter is None:
            self._game_setter = GameSetter(self.id, user)
        else:
            self._game_setter.join_user(user)
    
    def is_ready_to_start(self):
        return self._game_setter is not None and self._game_setter.is_ready()
    
    def start_game(self):
        self._game_setter.start_game()