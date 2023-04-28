# import .game_logic as game_logic
from ..game_logic import *
# from database_models import cur, conn, PlayerModel
import sys
# from ..application import Application
# app = Application()
from server import app
from .PlayerModel import *
cur = app.db.cur
conn = app.db.conn


class GameModel:
    def __init__(self, id, room_id):
        self.id = id
        self.room_id = room_id
        self.white_player = None
        self.black_player = None
        self.game = Game()
    
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
        game = GameModel(res[0], room_id)
        game.white_player = PlayerModel.make_new_player(white_user, game.id, True)
        game.black_player = PlayerModel.make_new_player(black_user, game.id, False)
        return game

    def handle_move(self, move):
        print('made move', file=sys.stderr)
        res = self.game.handle_move(move)
        if not res: return move
        cur.execute('''
            INSERT INTO turns (game_id, index, user_id, body)
            VALUES (%s, %s, %s, %s)
        ''', (self.id, 0, 
              self.white_player.user.id if move.is_white_player else self.black_player.user.id,
              str(move)))
        conn.commit()
        return move