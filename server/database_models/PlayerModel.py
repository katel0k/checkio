from database_models import cur, conn

class PlayerModel:
    def __init__(self, user, game_id, is_white):
        self.user = user
        self.game_id = game_id
        self.is_white = is_white

    @staticmethod
    def make_new_player(user, game_id, is_white):
        cur.execute('''
            INSERT INTO user_games
            (user_id, game_id, is_white) VALUES
            (%s, %s, %s)
        ''', (
            user.id, game_id, is_white
        ))
        conn.commit()
        return PlayerModel(user, game_id, is_white)