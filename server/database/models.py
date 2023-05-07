from enum import Enum
from flask_login import UserMixin

class UserModel(UserMixin):
    def __init__(self, id: int, **kwargs):
        self.id = id
        self.email: str = kwargs.get('email')
        self.password_hash: str = kwargs.get('password_hash')
        self.nickname: str = kwargs.get('nickname')
        self.rating: int = kwargs.get('rating')
        self.privileges: int = kwargs.get('privileges')
    
    def get_id(self):
        '''Необходимо для плагина flask_login'''
        return self.id

class RatingHistoryModel:
    def __init__(self, user_id: int, **kwargs):
        self.user_id = user_id
        self.changed_dttm: str = kwargs.get('changed_dttm')
        self.previous_rating: str = kwargs.get('previous_rating')

class RoomStates(Enum):
    WAITING = 'waiting'
    PLAYING = 'playing'
    DEAD = 'dead'

class RoomModel:
    def __init__(self, id: int, **kwargs):
        self.id = id
        self.state: RoomStates = kwargs.get('state', RoomStates.WAITING)
        self.created_dttm: str = kwargs.get('created_dttm')

class RoomHistoryModel:
    def __init__(self, room_id: int, **kwargs):
        self.user_id = room_id
        self.changed_dttm: str = kwargs.get('changed_dttm')
        self.previous_state: str = kwargs.get('previous_state')

class GameOutcomes(Enum):
    PLAYING = 'playing'
    WHITE_WON = 'white_won'
    BLACK_WON = 'black_won'
    DRAW = 'draw'
    CANCELLED = 'cancelled'

class GameModel:
    def __init__(self, id: int, room_id: int, **kwargs):
        self.id = id
        self.room_id = room_id
        self.outcome: GameOutcomes = kwargs.get('outcome', GameOutcomes.PLAYING)
        self.started_dttm: str = kwargs.get('started_dttm')

class TurnModel:
    def __init__(self, user_id: int, game_id: int, **kwargs):
        self.user_id = user_id
        self.game_id = game_id
        self.body = kwargs.get('body')
        self.dttm = kwargs.get('dttm')
        self.index = kwargs.get('index')

class UserGamesModel:
    def __init__(self, user_id: int, game_id: int, **kwargs):
        self.user_id = user_id
        self.game_id = game_id
        self.is_white: bool = kwargs.get('is_white')

class ViewerModel:
    def __init__(self, user_id: int, room_id: int, **kwargs):
        self.user_id = user_id
        self.room_id = room_id
        self.joined_dttm: str = kwargs.get('joined_dttm')
        self.left_dttm: str = kwargs.get('left_dttm')
    
class MessagesModel:
    def __init__(self, user_id: int, room_id: int, **kwargs):
        self.user_id = user_id
        self.room_id = room_id
        self.msg_body: str = kwargs.get('msg_body')
        self.dttm: str = kwargs.get('dttm')