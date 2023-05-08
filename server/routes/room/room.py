from server import app
from flask import session
from ...database import RoomModel
from ..dto import *
from .game_loop import GameLoop
from .user_manager import UserManager
socketio = app.socketio
server = app
# @socketio.on('disconnect')
# def disconnect_event_handler():
#     print(request.__dict__, file=sys.stderr)
#     print(session.__dict__, file=sys.stderr)
    
    # if not current_user.is_authenticated:
    #     return
    # room = current_user.current_room
    # print(room, file=sys.stderr)
    # print(current_user, file=sys.stderr)
    # if room is None:
    #     return
    # room.disconnect_user(current_user)
    # current_user.disconnect_room(room)
    # socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
    # for room in rooms():
    #     print(room, file=sys.stderr)
    #     leave_room(room)

# @socketio.on('client_disconnecting')
# def client_disconnecting_event_handler(room_id, user_id):
#     print(room_id, user_id, file=sys.stderr)
#     if room_id not in app.room_list: return
#     room = app.room_list[room_id]
#     user = User.load_user(user_id)
#     if not room.has_user(user): return
#     room.disconnect_user(user)
#     socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)

'''Эти обработчики необходимо добавлячть за пределами классов, чтобы они подгрузились'''

def add_room_event_handler(event_name):
    @socketio.on(event_name)
    def handle_event(*args, **kwargs):
        room = app.room_list[session['room_id']]
        return room.handle_event(event_name, *args, **kwargs)
    
add_room_event_handler('join_game')
add_room_event_handler('change_setting')
add_room_event_handler('made_move')
add_room_event_handler('left_game')

@socketio.on('join')
def handle_join_event(room_id, *args, **kwargs):
    session['room_id'] = room_id
    app.room_list[session['room_id']].handle_event('join', *args,  **kwargs)

class Room:
    def __init__(self, model: RoomModel):
        self.model: RoomModel = model
        self.__user_manager: UserManager = UserManager(self)
        self.game_loop: GameLoop = GameLoop(self)
    
    # FIXME: переделать, чтобы этот список лежал в комнате?
    def get_users(self):
        return self.__user_manager.get_users()

    def handle_event(self, event, *args, **kwargs):
        self.__user_manager.handle_event(event, *args, **kwargs)
        self.game_loop.handle_event(event, *args, **kwargs)
