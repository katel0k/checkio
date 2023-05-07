from server import app
from ..models import GameModel

conn = app.db.conn
cur = app.db.cur

# def make_new_game()