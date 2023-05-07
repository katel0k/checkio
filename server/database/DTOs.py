from .models import *

class UserDTO(dict):
    def __init__(self, user: UserModel):
        dict.__init__(
            self,
            id = user.id,
            email = user.email,
            nickname = user.nickname,
        )

# class RoomDTO(dict):
#     def __init__(self, room: RoomModel):
