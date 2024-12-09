from ...database import UserModel
from ...database.services import RoomService

from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from copy import copy

from server import app
socketio = app.socketio
from ..dto import *
from typing import Dict

from sys import stderr
def debug(*args):
    print(*args, file=stderr)

class UserManager:
    def __init__(self, room, users: Dict[int, UserModel] = dict()):
        self.users: Dict[int, UserModel] = users
        self.room = room

    def get_users(self) -> Dict[int, UserModel]:
        return self.users

    def has_user(self, user: UserModel):
        return user.id in self.users
    
    def __connect_user(self, user: UserModel):
        if self.has_user(user): return
        self.users[user.id] = user
        
    def __disconnect_user(self, user: UserModel):
        if not self.has_user(user): return
        self.users.pop(user.id)

# TODO: потенциально, код ниже можно убрать отсюда, чтобы сделать объект UserManager реюзабельным
# например, если я захочу добавить чат в лобби
    def handle_join_event(self):
        user = copy(current_user)
        self.__connect_user(user)
        join_room(self.room)
        RoomService.join_user(self.room.model, user)
        socketio.emit('player_joined', UserDTO(user), to=self.room)

    def handle_disconnect_event(self):
        user = copy(current_user)
        self.__disconnect_user(user)
        leave_room(self.room)
        RoomService.leave_user(self.room.model, user)
        socketio.emit('player_left', UserManagerDTO(self), to=self.room)
    
    def handle_event(self, event: str, *args, **kwargs):
        events_map = {
            'join': self.handle_join_event,
            'disconnect': self.handle_disconnect_event
        }
        if event not in events_map: return
        res = events_map[event](*args, **kwargs)
        socketio.emit('room_list_updated', (self.room.model.id, RoomDTO(self.room)), to=app.lobby)
        return res
