from flask import Flask
from config import Config
from random import randrange

# obviously bad code
ids_set = set()
def get_unique_id():
    x = randrange(10000)
    while x in ids_set:
        x = randrange(10000)
    return x
def del_unique_id(id):
    ids_set.remove(id)

class Game:
    pass

class Room:
    id = None
    player_1 = None
    player_2 = None
    game = None
    def __init__(self):
        pass

server = Flask(__name__, static_folder="../client")
server.config.from_object(Config)

class Application(object):
    room_list = {}
    def __init__(self):
        pass
    def get_room_list(self):
        return self.room_list
        
app = Application()



import models, routes