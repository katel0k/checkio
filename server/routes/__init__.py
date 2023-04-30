from .user import *
from .lobby import *
from .room import *

@server.route('/<path:path>')
@server.route('/room/<path:path>')
@server.route('/room/<int:game_id>/<path:path>')
def get_file(game_id, path):
    return send_from_directory('static', path)