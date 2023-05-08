from ..database import UserModel

# FIXME: этого здесь не должно быть
from flask_login import current_user

class UserDTO(dict):
    def __init__(self, user: UserModel):
        dict.__init__(
            self,
            id = user.id,
            nickname = user.nickname,
            rating = user.rating
        )

class UserManagerDTO(dict):
    def __init__(self, user_manager):
        dict.__init__(self,
            { user_id: UserDTO(user) for (user_id, user) in user_manager.users.items() } )

class RoomDTO(dict):
    def __init__(self, room):
        dict.__init__(self,
            id = room.model.id,
            state = room.model.state.value
        )
        self['user'] = UserDTO(current_user)
        self['viewers'] = UserManagerDTO(room.user_manager)

class GameDTO(dict):
    def __init__(self, game):
        dict.__init__(self, field = [[cell.__dict__ for cell in row] for row in game.field],
                      is_white_move = game.is_white_move)

class GameLoopDTO(dict):
    def __init__(self, game_loop):
        dict.__init__(self,
                      white_player = UserDTO(game_loop.white_player),
                      black_player = UserDTO(game_loop.black_player),
                      game = GameDTO(game_loop.game))