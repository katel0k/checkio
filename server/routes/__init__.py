from .user import *
from .lobby import *
from .room import *

@server.route('/<path:path>')
@server.route('/room/<path:path>')
def get_file(path):
    return send_from_directory('static', path)

@server.route('/room/<int:_>/<path:path>')
def get_file_(_, path):
    return send_from_directory('static', path)