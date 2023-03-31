from flask_login import UserMixin
from setup_db import cur, conn
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from sys import stderr
from server import login_manager

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
        self.email = kwargs['email']
        self._password_hash = kwargs['password_hash'] # да, костыль)) Нужен т.к. в бд хранятся только хеши
        self.nickname = kwargs['nickname']
        self.rating = kwargs['rating']

    def __update_field(self, field):
        cur.execute('''
            UPDATE users
            SET %s=%s WHERE id=%s
        ''', (field, self[field], self.id))
        conn.commit()

    @property
    def password(self):
        return self._password_hash
    @password.setter
    def password(self, value):
        self._password_hash = generate_password_hash(value)
        self.__update_field('password_hash')

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
    
    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, value):
        self._email = value
        self.__update_field('email')

    @property
    def nickname(self):
        return self._nickname
    @nickname.setter
    def nickname(self, value):
        self._nickname = value
        self.__update_field('nickname')

    @property
    def rating(self):
        return self._rating
    @rating.setter
    def rating(self, value):
        self._rating = value
        self.__update_field('rating')


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





# class ActivePlayer:
#     def __init__(self):
#         pass
#     def __repr__(self):
#         return self.__str__()