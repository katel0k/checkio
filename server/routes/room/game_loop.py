from ...database import UserModel, RoomStates, GameModel
from ...database.services import RoomService, GameService
from .game_logic import Game, GameMove

from flask_login import current_user
from flask_socketio import emit
from copy import copy

from server import app
socketio = app.socketio
from ..dto import *

import json


class GameLoop:
    def __init__(self, room):
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


