# from .application import Application
from .application import create_app
app = create_app()
# app = Application()
# import sys
# print(app, file=sys.stderr)
# app.run()

# from flask import appcontext_tearing_down
# appcontext_tearing_down.connect(app.db.close, app.server)

from .routes import *

# app.room_list = models.Room.get_from_database()