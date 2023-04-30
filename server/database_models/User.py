from flask_login import UserMixin
from psycopg2 import sql
from server import app
from werkzeug.security import generate_password_hash, check_password_hash

cur = app.db.cur
conn = app.db.conn

class LoginError(Exception):
    '''Такая ошибка происходит при неудачной попытке входа в аккаунт'''
    def __init__(self, msg=None):
        super().__init__(msg)

class RegisterError(Exception):
    '''Такая ошибка происходит при неудачной попытке регистрации пользователя'''
    def __init__(self, msg=None):
        super().__init__(msg)

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
    @app.login_manager.user_loader
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
        return 'id: %s, email: %s, nickname: %s' % (self.id, self.email, self.nickname)
    def __repr__(self):
        return self.__str__()
    def __json__(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'rating': self.rating
        }