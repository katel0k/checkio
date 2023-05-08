from enum import Enum
from flask_login import UserMixin

class UserModel(UserMixin):
    def __init__(self, id: int, email: str, password_hash: str, nickname: str, rating: int, privileges: int):
        self.id: int = id
        self.email: str = email
        self.password_hash: str = password_hash
        self.nickname: str = nickname
        self.rating: int = rating
        self.privileges: int = privileges
    
    def get_id(self) -> int:
        '''Необходимо для плагина flask_login'''
        return self.id

    # FIXME: ЗАГЛУШКА УБРАТЬ ДЕЛЕТЕ
    def __json__(self) -> str:
        return ''

class RatingHistoryModel:
    def __init__(self, user_id: int, changed_dttm: str, previous_rating: str):
        self.user_id: int = user_id
        self.changed_dttm: str = changed_dttm
        self.previous_rating: str = previous_rating

class RoomStates(Enum):
    WAITING = 'WAITING'
    PLAYING = 'PLAYING'
    DEAD = 'DEAD'
    @staticmethod
    def from_db_record(value: str):
        if value == RoomStates.WAITING.value: return RoomStates.WAITING
        if value == RoomStates.DEAD.value: return RoomStates.DEAD
        if value == RoomStates.PLAYING.value: return RoomStates.PLAYING

class RoomModel:
    def __init__(self, id: int, state: RoomStates, created_dttm: str):
        self.id: int = id
        self.state: RoomStates = state
        self.created_dttm: str = created_dttm

class RoomHistoryModel:
    def __init__(self, room_id: int, changed_dttm: str, previous_state: str):
        self.room_id: int = room_id
        self.changed_dttm: str = changed_dttm
        self.previous_state: str = previous_state

class GameOutcomes(Enum):
    PLAYING = 'PLAYING'
    WHITE_WON = 'WHITE_WON'
    BLACK_WON = 'BLACK_WON'
    DRAW = 'DRAW'
    CANCELLED = 'CANCELLED'
    def from_db_record(value: str):
        if value == GameOutcomes.WHITE_WON.value: return GameOutcomes.WHITE_WON
        if value == GameOutcomes.BLACK_WON.value: return GameOutcomes.BLACK_WON
        if value == GameOutcomes.DRAW.value: return GameOutcomes.DRAW
        if value == GameOutcomes.CANCELLED.value: return GameOutcomes.CANCELLED
        if value == GameOutcomes.PLAYING.value: return GameOutcomes.PLAYING

class GameModel:
    def __init__(self, id: int, room_id: int, outcome: GameOutcomes, started_dttm: str):
        self.id: int = id
        self.room_id: int = room_id
        self.outcome: GameOutcomes = outcome
        self.started_dttm: str = started_dttm

class TurnModel:
    def __init__(self, user_id: int, game_id: int, body: str, dttm: str, index: int):
        self.user_id: int = user_id
        self.game_id: int = game_id
        self.body: str = body
        self.dttm: str = dttm
        self.index: int = index

class UserGamesModel:
    def __init__(self, user_id: int, game_id: int, is_white: bool):
        self.user_id: int = user_id
        self.game_id: int = game_id
        self.is_white: bool = is_white

class ViewerModel:
    def __init__(self, user_id: int, room_id: int, joined_dttm: str, left_dttm: str = None):
        self.user_id: int = user_id
        self.room_id: int = room_id
        self.joined_dttm: str = joined_dttm
        self.left_dttm: str = left_dttm
    
class MessagesModel:
    def __init__(self, user_id: int, room_id: int, msg_body: str, dttm: str):
        self.user_id: int = user_id
        self.room_id: int = room_id
        self.msg_body: str = msg_body
        self.dttm: str = dttm