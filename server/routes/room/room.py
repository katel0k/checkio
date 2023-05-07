from server import app
from flask_login import current_user
from flask_socketio import join_room, emit
from flask import session
from typing import Dict

from ...database import RoomModel, UserModel
from ...database.services import RoomService
from ...database.DTOs import UserDTO

socketio = app.socketio
server = app

import sys
from copy import copy
import json

from .game_logic import GameMove


# @socketio.on('join')
# def join_event_handler(room_id):
#     room = app.room_list[room_id]
#     room.connect_user(current_user)
#     join_room(room)
#     socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
#     socketio.emit('player_joined', {
#         user_id: {
#             'nickname': viewer.user.nickname
#         } for (user_id, viewer) in room.viewers.items()
#     }, to=room)


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

# @socketio.on('join_game')
# def join_game_event_handler(room_id):
#     room = app.room_list[room_id]
#     if room.is_player_set(current_user): return

#     room.set_player(copy.copy(current_user))
#     socketio.emit('player_set', {
#         'id': current_user.id,
#         'nickname': current_user.nickname,
#         'rating': current_user.rating
#     }, to=room)
#     # print(room.is_ready_to_start(), file=sys.stderr)
#     # print(room.white_player, file=sys.stderr)
#     # print(room.black_player, file=sys.stderr)
#     if room.is_ready_to_start():
#         room.start_game()
#         socketio.emit('game_started',
#             {
#             'white_player': room.white_player.__json__(),
#             'black_player': room.black_player.__json__(),
#             'game': { 'id': room.get_game()['id'] }
#             }, to=room)

# @socketio.on('made_move')
# def move_handler(room_id, move):
#     room = app.room_list[room_id]
#     move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
#     # если клиент отправит ход от неправильного игрока, там будет None
#     if move.is_white_player is not None:
#         move = room.handle_move(move)
#     emit('made_move', json.dumps({
#         'game': room.get_game(),
#         'move': move
#         }, default=lambda o: o.__dict__, 
#             sort_keys=True, indent=4), to=room)

# from ...database import ViewerModel

'''Эти обработчики необходимо добавлячть за пределами классов, чтобы они подгрузились'''

def add_room_event_handler(event_name):
    @socketio.on(event_name)
    def handle_event(*args, **kwargs):
        room = app.room_list[session['room_id']]
        return room.handle_event(event_name, *args, **kwargs)
    
add_room_event_handler('join_game')
add_room_event_handler('made_move')

@socketio.on('join')
def handle_join_event(room_id, *args, **kwargs):
    session['room_id'] = room_id
    app.room_list[session['room_id']].handle_event('join', *args,  **kwargs)


class Room:
    def __init__(self, model: RoomModel):
        self.model: RoomModel = model
        self.__user_manager: UserManager = UserManager(self)
        # self.__game_loop: GameLoopStartegy = 
    
    # FIXME: переделать, чтобы этот список лежал в комнате?
    def get_users(self):
        return self.__user_manager.get_users()

    def handle_event(self, event, *args, **kwargs):
        self.__user_manager.handle_event(event, *args, **kwargs)
        # self.__game_loop.handle_event(event, *args, **kwargs)

class RoomDTO(dict):
    def __init__(self, room: Room):
        dict.__init__(self,
            id = room.model.id,
            state = room.model.state
        )
        self['user'] = UserDTO(current_user)
        self['viewers'] = {
            user_id: UserDTO(user) for (user_id, user) in room.get_users()
        }


class UserManager:
    '''Вспомогательный класс для класса RoomModel. Менеджит всех людей в комнате(наблюдателей)
    Эти люди точно будут получать уведомления, о том, что происходит в комнате и о них должны быть записи в БД'''
    def __init__(self, room: Room, users: Dict[int, UserModel] = dict()):
        self.__users: Dict[int, UserModel] = users
        self.__room: Room = room

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
        socketio.emit('room_list_updated', (self.__room.model.id, self.__room.model.state, len(self.__users)), to=app.lobby)
        return res

class GameLoopStartegy:
    def __init__(self, room: Room):
        self.__room = room
    def handle_event(self, event: str, *args, **kwargs):
        pass

# @socketio.on('join')
# def join_event_handler(room_id):
#     session['room_id'] = room_id
#     room = app.get_room(room_id)
