from flask_login import UserMixin

class User(UserMixin):
    id = 1
    FIO = 'hello'
    def __init__(self, id):
        self.id = id