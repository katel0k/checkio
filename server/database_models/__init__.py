# import models
import psycopg2
from flask import appcontext_tearing_down
from server import app

conn = psycopg2.connect(user='postgres', 
                        host='172.17.0.2', port='5432', password='admin')

cur = conn.cursor()

def close_db_connection(sender, **extra):
    cur.close()
    conn.close()

appcontext_tearing_down.connect(close_db_connection, app)


# этот порядок специфичен, не трогать
from .User import *
from .PlayerModel import *
from .GameModel import *

from .ViewerModel import *
from .RoomModel import *


# from flask_login import UserMixin
# from setup_db import cur, conn
# from enum import Enum
# from werkzeug.security import generate_password_hash, check_password_hash
# from sys import stderr
# from server import login_manager
# from psycopg2 import sql
# import game_logic
# import sys
# import json








