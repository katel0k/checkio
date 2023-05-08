from server import app
from ..models import GameModel, RoomModel, UserModel, TurnModel, GameOutcomes

conn = app.db.conn
cur = app.db.cur



def make_new_game(room: RoomModel, white_player: UserModel, black_player: UserModel) -> GameModel:
    cur.execute('''
            INSERT INTO games (room_id) VALUES (%s)
            RETURNING id, room_id, outcome, started_dttm
        ''', (room.id, ))
    res = cur.fetchone()
    id = res[0]
    
    cur.execute('''
        INSERT INTO user_games (game_id, user_id, is_white) 
        VALUES (%s, %s, True), (%s, %s, False)
    ''', (id, white_player.id, id, black_player.id))

    conn.commit()
    return GameModel(
        id = res[0],
        room_id = res[1],
        outcome = res[2],
        started_dttm = res[3]
    )

def make_new_move(game: GameModel, body: str, index: int, user: UserModel) -> TurnModel:
    res = cur.execute('''
        INSERT INTO turns (user_id, game_id, body, index)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id, game_id, body, dttm, index
    ''', (
        user.id, game.id, body, index
    ))
    conn.commit()
    return TurnModel(
        user_id = res[0],
        game_id = res[1],
        body = res[2],
        dttm = res[3],
        index = res[4]
    )

def change_outcome(game: GameModel, new_outcome: GameOutcomes):
    cur.execute('''UPDATE games SET outcome=%s WHERE id=%s''', (new_outcome, game.id))
    cur.execute('''UPDATE users SET rating=rating+1
      FROM (
        SELECT users.id FROM users JOIN user_games ON (users.id = user_games.user_id)
        WHERE %s='WHITE_WON' AND is_white OR %s='BLACK_WON' AND NOT is_white
    ) AS valid_users WHERE valid_users.id = users.id''')
    conn.commit()
