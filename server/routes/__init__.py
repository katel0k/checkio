# из этих файлов надо просто выполнить код
# модульная система питона не позволит просто написать import .user
from .user import *
from .lobby import *
from .room import *
from flask import send_from_directory

@server.route('/<path:path>')
@server.route('/room/<path:path>')
def get_file(path):
    return send_from_directory('static', path)

@server.route('/room/<int:_>/<path:path>')
def get_file_(_, path):
    return send_from_directory('static', path)