from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from .db_engine import DB

_instance = None
def create_app(**kwargs):
    if _instance is not None:
        return _instance
    
    server = Flask(__name__,
                    static_folder=kwargs['STATIC_FOLDER'],
                    template_folder=kwargs['TEMPLATE_FOLDER'])
    
    server.config['SECRET_KEY'] = kwargs['SECRET_KEY']

    server.login_manager = LoginManager(server)
    server.login_manager.login_view = 'load_user'

    server.socketio = SocketIO(server)

    server.db = DB(**kwargs)
    
    server.room_list = {}

    return server
