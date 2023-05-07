from server import app
from flask_login import current_user
from flask_socketio import join_room, emit
from flask import session
from typing import Dict

from ...database import RoomStates, RoomModel, UserModel, GameModel
from ...database.services import RoomService, GameService
from ...database.services.UserService import UserDTO

socketio = app.socketio
server = app

import sys
from copy import copy
import json

from .game_logic import GameMove, Game

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
        socketio.emit('room_list_updated', (self.__room.model.id, RoomDTO(self.__room)), to=app.lobby)
        return res


class GameLoop:
    def __init__(self, room: Room):
        self.room = room
        self.__strategy: GameLoopStrategy = GameLoopSetupStrategy(self)
        self.white_player: UserModel = None
        self.black_player: UserModel = None
        self.game: Game = None
        self.game_model: GameModel = None
        
    def handle_event(self, event: str, *args, **kwargs):
        self.__strategy.handle_event(event, *args, **kwargs)
    
    def change_strategy(self, new_strategy):
        self.__strategy = new_strategy
    
    def is_player_set(self, user: UserModel):
        return self.white_player == user or self.black_player == user
    
    def set_player(self, user: UserModel):
        if self.white_player is None:
            self.white_player = user
        elif self.black_player is None:
            self.black_player = user
    
    def is_ready_to_start(self) -> bool:
        return self.white_player is not None and self.black_player is not None

class GameLoopStrategy:
    def __init__(self, game_loop: GameLoop):
        self.game_loop = game_loop
    def handle_event(self, event: str, *args, **kwargs):
        pass

class GameLoopSetupStrategy(GameLoopStrategy):
    def __init__(self, game_loop: GameLoop):
        super().__init__(game_loop)
        self.game_loop.game_model = None
        self.game_loop.game = None

    def handle_join_game_event(self, *args, **kwargs):
        if self.game_loop.is_player_set(current_user): return
        self.game_loop.set_player(copy(current_user))

        room = self.game_loop.room

        socketio.emit('player_set', {
            'id': current_user.id,
            'nickname': current_user.nickname,
            'rating': current_user.rating
        }, to=room)
        if self.game_loop.is_ready_to_start():
            RoomService.change_state(self.game_loop.room.model, RoomStates.PLAYING)
            self.game_loop.change_strategy(GameLoopPlayingStrategy(self.game_loop))
            socketio.emit('game_started', GameLoopDTO(self.game_loop), to=room)


    def handle_event(self, event: str, *args, **kwargs):
        events_map = {
            'join_game': self.handle_join_game_event
        }
        if event not in events_map: return
        res = events_map[event](*args, **kwargs)
        return res

class GameLoopPlayingStrategy(GameLoopStrategy):
    def __init__(self, game_loop: GameLoop):
        # TODO: добавить здесь параметры игры
        super().__init__(game_loop)
        self.game_loop.game_model = GameService.make_new_game(
            self.game_loop.room.model, self.game_loop.white_player, self.game_loop.black_player)
        self.game_loop.game = Game()

    def handle_move_event(self, move, *args, **kwargs):
        move: GameMove = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
        if move.is_white_player is None: return

        move = self.game_loop.game.handle_move(move)
        if move.is_possible:
            GameService.make_new_move(self.game_loop.game_model, str(move), len(self.game_loop.game.history), 
                    self.game_loop.white_player if move.is_white_player else self.game_loop.black_player)

        emit('made_move', json.dumps({
            'game': GameDTO(self.game_loop.game),
            'move': move
            }, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4), to=self.game_loop.room)

    def handle_event(self, event: str, *args, **kwargs):
        events_map = {
            'made_move': self.handle_move_event
        }
        if event not in events_map: return
        res = events_map[event](*args, **kwargs)
        return res




class RoomDTO(dict):
    def __init__(self, room: Room):
        dict.__init__(self,
            id = room.model.id,
            state = room.model.state
        )
        self['user'] = UserDTO(current_user)
        self['viewers'] = {
            user_id: UserDTO(user) for (user_id, user) in room.get_users().items()
        }

class GameDTO(dict):
    def __init__(self, game: Game):
        dict.__init__(self, field = [[cell.__dict__ for cell in row] for row in game.field],
                      is_white_move = game.is_white_move)

class GameLoopDTO(dict):
    def __init__(self, game_loop: GameLoop):
        dict.__init__(self,
                      white_player = UserDTO(game_loop.white_player),
                      black_player = UserDTO(game_loop.black_player),
                      game = GameDTO(game_loop.game))