from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from .db_engine import DB
from .config import config

_instance = None
def create_app(**kwargs):
    if _instance is not None:
        return _instance
    
    server = Flask(__name__, static_folder="../client", template_folder="../client/templates")
    server.config['SECRET_KEY'] = config['SECRET_KEY']

    server.login_manager = LoginManager(server)
    server.login_manager.login_view = 'load_user'

    server.socketio = SocketIO(server, ping_timeout=10000, logger=False)

    server.db = DB(**kwargs)
    server.room_list = {}

    return server