from flask import Flask
from flask_login import LoginManager
from config import Config
from random import randrange
from flask_socketio import SocketIO
import game_logic

# obviously bad code
ids_set = set()
def get_unique_id():
    x = randrange(10000)
    while x in ids_set:
        x = randrange(10000)
    ids_set.add(x)
    return x
def del_unique_id(id):
    ids_set.remove(id)

class Room:
    id = None
    player1 = None
    player2 = None
    game = None
    def __init__(self):
        self.id = get_unique_id()

server = Flask(__name__, static_folder="../client", template_folder="../client/templates")
server.config.from_object(Config)

login_manager = LoginManager(server)
login_manager.login_view = 'load_user'

socketio = SocketIO(server, ping_timeout=10000)

class Application(object):
    room_list = {}
    def __init__(self):
        pass
    def get_room_list(self):
        return self.room_list
        
app = Application()

game_engine = game_logic.GameEngine()

import models, routes