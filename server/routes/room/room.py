from server import app
from flask import session
from ...database import RoomModel, RoomStates
from ...database.services import RoomService
from ..dto import *
from .game_loop import GameLoop
from .user_manager import UserManager
socketio = app.socketio
server = app

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

@socketio.on('disconnect')
def handle_disconnect():
    if 'room_id' not in session:
        return
    room = app.room_list[session['room_id']]
    room.handle_event('disconnect')
    if len(room.user_manager.users) == 0:
        app.room_list.pop(room.model.id)
        room.update_state(RoomStates.DEAD)

# обработчик этого события отличается от других, потому что он кладет в сессию айдишник комнаты
@socketio.on('join')
def handle_join_event(room_id, *args, **kwargs):
    session['room_id'] = room_id
    app.room_list[session['room_id']].handle_event('join', *args,  **kwargs)

class Room:
    def __init__(self, model: RoomModel):
        self.model: RoomModel = model
        self.user_manager: UserManager = UserManager(self)
        self.game_loop: GameLoop = GameLoop(self)
    
    def get_users(self):
        return self.user_manager.get_users()

    def handle_event(self, event, *args, **kwargs):
        self.user_manager.handle_event(event, *args, **kwargs)
        self.game_loop.handle_event(event, *args, **kwargs)

    def update_state(self, new_state: RoomStates):
        RoomService.change_state(self.game_loop.room.model, new_state)
        socketio.emit('room_list_updated', (self.model.id, RoomDTO(self)), to=app.lobby)