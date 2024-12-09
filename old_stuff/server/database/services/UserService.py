from server import app
from ..models import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

conn = app.db.conn

def make_user(user_tuple: tuple | None) -> UserModel | None:
    '''Все функции ниже используют вызовы из постгреса, возвращающие формат
    id, email, password_hash, nickname, rating, privileges. Эта функция для того чтобы убрать повторение'''
    if user_tuple is None: return None
    return UserModel(
        user_tuple[0],
        email = user_tuple[1],
        password_hash = user_tuple[2],
        nickname = user_tuple[3],
        rating = user_tuple[4],
        privileges = user_tuple[5]
    )

@app.login_manager.user_loader
def load_user(id: int):
    cur = conn.cursor()
    cur.execute(
        '''SELECT id, email, password_hash, nickname, rating, privileges
            FROM users WHERE id=%s''', (id, ))
    user_tuple = cur.fetchone()
    return make_user(user_tuple)

def register_new_user(email: str, password: str, nickname: str) -> UserModel | None:
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO users 
            (email, password_hash, nickname) 
            VALUES (%s, %s, %s)
            RETURNING id, email, password_hash, nickname, rating, privileges''',
        (email,
            generate_password_hash(password),
            nickname)
    )
    conn.commit()
    user_tuple = cur.fetchone()
    return make_user(user_tuple)

def get_user(email: str, password: str) -> UserModel | None:
    cur = conn.cursor()
    cur.execute(
        '''SELECT id, email, password_hash, nickname, rating, privileges
            FROM users WHERE email=%s''', (email, ))
    user_tuple = cur.fetchone()
    if not check_password_hash(user_tuple[2], password):
        return None
    return make_user(user_tuple)

def get_user_info(user: UserModel):
    cur = conn.cursor()
    cur.execute('''SELECT game_id, outcome, is_white
    FROM full_game_info WHERE user_id=%s''', (user.id, ))
    res = {}
    for game in cur.fetchall():
        res[game[0]] = {
            'outcome': game[1],
            'is_white': game[2]
        }
    return res

def get_user_rating_graph(user: UserModel):
    cur = conn.cursor()
    cur.execute('''SELECT previous_rating, changed_dttm
      FROM users JOIN rating_history ON (users.id = rating_history.user_id)
    WHERE user_id=%s 
    ''', (user.id, ))

    dates = []
    values = []
    for rating, date in cur.fetchall():
        dates.append(date)
        values.append(rating)

    return dates, values

__all__ = ['register_new_user', 'get_user', 'get_user_info', 'get_user_rating_graph']
