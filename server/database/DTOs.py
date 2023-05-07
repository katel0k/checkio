from .models import *

class UserDTO(dict):
    def __init__(self, user: UserModel):
        dict.__init__(
            self,
            id = user.id,
            nickname = user.nickname,
            rating = user.rating
        )



# class RoomDTO(dict):
#     def __init__(self, room: RoomModel):
