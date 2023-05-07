from server import app
from ..models import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

conn = app.db.conn
cur = app.db.cur

def make_user(user_tuple: tuple | None) -> UserModel | None:
    '''Все функции ниже используют вызовы из постгреса, возвращающие формат
    id, email, password_hash, nickname, rating. Эта функция для того чтобы убрать повторение'''
    if user_tuple is None: return None
    return UserModel(
        user_tuple[0],
        email = user_tuple[1],
        password_hash = user_tuple[2],
        nickname = user_tuple[3],
        rating = user_tuple[4],
    )

@app.login_manager.user_loader
def load_user(id: int):
    cur.execute(
        '''SELECT id, email, password_hash, nickname, rating
            FROM users WHERE id=%s''', (id, ))
    user_tuple = cur.fetchone()
    return make_user(user_tuple)

def register_new_user(email: str, password: str, nickname: str) -> UserModel | None:
    cur.execute(
        '''INSERT INTO users 
            (email, password_hash, nickname) 
            VALUES (%s, %s, %s)
            RETURNING id, email, password_hash, nickname, rating''',
        (email,
            generate_password_hash(password),
            nickname)
    )
    user_tuple = cur.fetchone()
    return make_user(user_tuple)

def get_user(email: str, password: str) -> UserModel | None:
    cur.execute(
        '''SELECT id, email, password_hash, nickname, rating
            FROM users WHERE email=%s''', (email, ))
    user_tuple = cur.fetchone()
    if not check_password_hash(user_tuple[2], password):
        return None
    return make_user(user_tuple)

__all__ = ['register_new_user', 'get_user']