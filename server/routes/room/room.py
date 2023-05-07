from server import app
from flask_login import current_user
from flask_socketio import join_room, emit
socketio = app.socketio
server = app

import sys
import copy
import json

from .game_logic import GameMove


@socketio.on('join')
def join_event_handler(room_id):
    room = app.room_list[room_id]
    room.connect_user(current_user)
    join_room(room)
    socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
    socketio.emit('player_joined', {
        user_id: {
            'nickname': viewer.user.nickname
        } for (user_id, viewer) in room.viewers.items()
    }, to=room)


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

@socketio.on('join_game')
def join_game_event_handler(room_id):
    room = app.room_list[room_id]
    if room.is_player_set(current_user): return

    room.set_player(copy.copy(current_user))
    socketio.emit('player_set', {
        'id': current_user.id,
        'nickname': current_user.nickname,
        'rating': current_user.rating
    }, to=room)
    # print(room.is_ready_to_start(), file=sys.stderr)
    # print(room.white_player, file=sys.stderr)
    # print(room.black_player, file=sys.stderr)
    if room.is_ready_to_start():
        room.start_game()
        socketio.emit('game_started',
            {
            'white_player': room.white_player.__json__(),
            'black_player': room.black_player.__json__(),
            'game': { 'id': room.get_game()['id'] }
            }, to=room)

@socketio.on('made_move')
def move_handler(room_id, move):
    room = app.room_list[room_id]
    move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
    # если клиент отправит ход от неправильного игрока, там будет None
    if move.is_white_player is not None:
        move = room.handle_move(move)
    emit('made_move', json.dumps({
        'game': room.get_game(),
        'move': move
        }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4), to=room)

# from ...database import ViewerModel

# class ViewerManager:
#     '''Вспомогательный класс для класса RoomModel. Менеджит всех людей в комнате(наблюдателей)
#     Эти люди точно будут получать уведомления, о том, что происходит в комнате и о них должны быть записи в БД'''
#     def __init__(self, room, **kwargs):
#         '''Конструктор может получить на вход viewers - словарь пользователей, если комната подгружается из БД'''
#         self._viewers = kwargs.get('viewers', dict())
#         self._room = room

#     def has_user(self, user):
#         return user.id in self.viewers
    
#     def connect_user(self, user):
#         if self.has_user(user): return
#         self.viewers[user.id] = ViewerModel.make_new_viewer(user, self._room)
        
#     def disconnect_user(self, user):
#         if not user.id in self.viewers: return
#         viewer = self.viewers[user.id]
#         viewer.leave_room()
#         self.viewers.pop(user.id)
    
#     @property
#     def viewers(self):
#         return self._viewers


# class Room:
#     def __init__(self, model):
#         self.__model = model
