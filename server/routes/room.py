from ..database_models import *
from server import app
from flask import request, render_template, send_from_directory, redirect, make_response, session
from flask_socketio import emit, join_room, leave_room, rooms
from flask_login import current_user
import json

from ..game_logic import GameMove
import sys
import copy

server = app
socketio = app.socketio

@server.route('/room/<int:room_id>/')
def room_id_route(room_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    
    if room_id not in app.room_list:
        return redirect('/')

    if request.method != 'GET':
        return redirect('/')

    return render_template('room.html', title="Game", room_id=room_id)

@server.route('/room/<int:room_id>/info')
def room_id_info_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')
    room = app.room_list[room_id]
    if room._game_setter is None:
        return json.dumps({
            'id': room_id,
            'state': room._state,
            'white_player': None,
            'black_player': None,
            'viewers': {
                user_id: {
                    'nickname': viewer.user.nickname
                } for (user_id, viewer) in room.viewers.items()
            },
            'user': {
                'id': current_user.id
            }
        }, default=lambda o: o.__dict__, 
        sort_keys=True, indent=4)
    elif room._game_setter.is_playing():
        return json.dumps({
            'id': room_id,
            'state': room._state,
            'white_player': room._game_setter.game.white_player.user,
            'black_player': room._game_setter.game.black_player.user,
            'viewers': {
                user_id: {
                    'nickname': viewer.user.nickname
                } for (user_id, viewer) in room.viewers.items()
            },
            'user': {
                'id': current_user.id
            }
        }, default=lambda o: o.__dict__, 
        sort_keys=True, indent=4)
    else:
        return json.dumps({
            'id': room_id,
            'state': room._state,
            'white_player': room._game_setter.creator,
            'black_player': room._game_setter.opponent,
            'viewers': {
                user_id: {
                    'nickname': viewer.user.nickname
                } for (user_id, viewer) in room.viewers.items()
            },
            'user': {
                'id': current_user.id
            }
        }, default=lambda o: o.__dict__, 
        sort_keys=True, indent=4)

@server.route('/room/<int:room_id>/leave')
def room_id_leave_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')

    if not current_user.is_authenticated:
        return redirect('/login')
    
    room = app.room_list[room_id]

    if room.player1 == current_user.get_id():
        room.player1, room.player2 = room.player2, None
        emit('player_left', to=room)
        # TODO
    elif room.player2 == current_user.get_id():
        room.player2 = None
        emit('player_left', to=room)
        # TODO

    return redirect('/')

@server.route('/room/<int:room_id>/game')
def room_id_game_route(room_id):
    if room_id not in app.room_list:
        return make_response('Incorrect room id, no such room exists', 400)
    game_obj = app.room_list[room_id]._game_setter.game
    return json.dumps({
        'field': game_obj.game.field,
        'order': game_obj.game.is_white_move,
        'white_player': game_obj.white_player.user,
        'black_player': game_obj.black_player.user
    }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


@socketio.on('join')
def join_event_handler(room_id):
    room = app.room_list[room_id]
    room.connect_user(current_user)
    join_room(room)
    socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
    socketio.emit('player_joined', {
        user_id: {
            'nickname': viewer.user.nickname
        } for (user_id, viewer) in room.viewers.items()
    }, to=room)


# @socketio.on('disconnect')
# def disconnect_event_handler():
#     print(request.__dict__, file=sys.stderr)
#     print(session.__dict__, file=sys.stderr)
    
    # if not current_user.is_authenticated:
    #     return
    # room = current_user.current_room
    # print(room, file=sys.stderr)
    # print(current_user, file=sys.stderr)
    # if room is None:
    #     return
    # room.disconnect_user(current_user)
    # current_user.disconnect_room(room)
    # socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
    # for room in rooms():
    #     print(room, file=sys.stderr)
    #     leave_room(room)

# @socketio.on('client_disconnecting')
# def client_disconnecting_event_handler(room_id, user_id):
#     print(room_id, user_id, file=sys.stderr)
#     if room_id not in app.room_list: return
#     room = app.room_list[room_id]
#     user = User.load_user(user_id)
#     if not room.has_user(user): return
#     room.disconnect_user(user)
#     socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)

@socketio.on('join_game')
def join_game_event_handler(room_id):
    room = app.room_list[room_id]
    room.set_player(copy.copy(current_user))
    socketio.emit('player_set', {
        'id': current_user.id,
        'nickname': current_user.nickname,
        'rating': current_user.rating
    }, to=room)
    # TODO: make an error when same player tries to connect
    if room.is_ready_to_start():
        room.start_game()
        game = room._game_setter.game
        # room._game_setter.game
        socketio.emit('ready_to_start',
                      {
            'white_player': {
                'id': game.white_player.user.id,
                'nickname': game.white_player.user.nickname,
                'rating': game.white_player.user.rating
            },
            'black_player': {
                'id': game.black_player.user.id,
                'nickname': game.black_player.user.nickname,
                'rating': game.black_player.user.rating
            },
            'game': {
                'id': game.id
            }
                      },
                       to=room)

@socketio.on('made_move')
def move_handler(room_id, move):
    room = app.room_list[room_id]
    # room._game_setter.game.handle_move(move)
    move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
    # game_engine.handle_move(room._game_setter.game.game, move)
    move = room._game_setter.game.handle_move(move)
    emit('made_move', json.dumps({
        'field': room._game_setter.game.game.field, 'move': move
        }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4), to=room)

@server.route('/user')
def user_route():
    return current_user.id # TODO

@server.route('/user/<int:user_id>')
def user_by_id_route(user_id):
    return current_user.id # TODO

@server.route('/<path:path>')
@server.route('/room/<path:path>')
def get_file(path):
    return send_from_directory('static', path)