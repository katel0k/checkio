from flask import Flask, appcontext_tearing_down
from flask_login import LoginManager
from flask_socketio import SocketIO
from .db_engine import DB

_instance = None
def create_app():
    if _instance is not None:
        return _instance
    
    server = Flask(__name__, static_folder="../client", template_folder="../client/templates")
    # self.server.config.from_object('config')
    server.config['SECRET_KEY'] = 'shaurma' # remove config from here

    server.login_manager = LoginManager(server)
    server.login_manager.login_view = 'load_user'

    server.socketio = SocketIO(server, ping_timeout=10000, logger=False)

    server.db = DB()
    # server.teardown_appcontext(server.db.close)
    server.room_list = {}

    return server



# class Application(object):
#     _instance = None
#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = object.__new__(cls)
#         return cls._instance
    
#     def __init__(self):
#         self.server = Flask(__name__, static_folder="../client", template_folder="../client/templates")
#         # self.server.config.from_object('config')
#         self.server.config['SECRET_KEY'] = 'shaurma' # remove config from here

#         self.login_manager = LoginManager(self.server)
#         self.login_manager.login_view = 'load_user'

#         self.socketio = SocketIO(self.server, ping_timeout=10000, logger=False)

#         self.db = DB()
#         self.server.teardown_appcontext(self.db.close)
#         self.room_list = {}

#     def get_room_list(self):
#         return self.room_list
    
#     def __del__(self):
#         # мне очень интенресно, почему от банального перетаскивания этой строчки в другое место,
#         # сигнал appcontext_tearing_down перестал работать адекватно. Но он стал посылаться после каждого
#         # HTTP запроса, что, очевидно, неправильно. Мб из-за каких-то ошибок, не знаю
#         # в связи с этим я перетащил закрытие бд временно сюда, ибо это вроде должно быть тем же самым
#         self.db.close()