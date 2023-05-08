from ...database import UserModel
from ...database.services import RoomService

from flask_login import current_user
from flask_socketio import emit, join_room
from copy import copy

from server import app
socketio = app.socketio
from ..dto import *
from typing import Dict

class UserManager:
    '''Вспомогательный класс для класса RoomModel. Менеджит всех людей в комнате(наблюдателей)
    Эти люди точно будут получать уведомления, о том, что происходит в комнате и о них должны быть записи в БД'''
    def __init__(self, room, users: Dict[int, UserModel] = dict()):
        self.__users: Dict[int, UserModel] = users
        self.__room = room

    def get_users(self) -> Dict[int, UserModel]:
        return self.__users

    def has_user(self, user: UserModel):
        return user.id in self.__users
    
    def __connect_user(self, user: UserModel):
        if self.has_user(user): return
        RoomService.join_user(self.__room.model, user)
        self.__users[user.id] = user
        
    def __disconnect_user(self, user: UserModel):
        if not user.id in self.__users: return
        user = self.__users[user.id]
        RoomService.leave_user(self.__room.model, user)
        self.__users.pop(user.id)

    def handle_join_event(self):
        user = copy(current_user)
        self.__connect_user(user)
        join_room(self.__room)
        socketio.emit('player_joined', UserDTO(user), to=self.__room)
    
    def handle_event(self, event: str, *args, **kwargs):
        events_map = {
            'join': self.handle_join_event
        }
        if event not in events_map: return
        res = events_map[event](*args, **kwargs)
        # FIXME: переделать с использованием DTO
        socketio.emit('room_list_updated', (self.__room.model.id, RoomDTO(self.__room)), to=app.lobby)
        return res

