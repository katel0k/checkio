from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email):
        super()
        self.email = email

    def get_id(self):
        return self.email # TODO: temporary

    def get_from_DB(db_tuple):
        u = User(db_tuple[1]) # TODO: omg wtf
        return u
