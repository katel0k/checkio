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
    return json.dumps({
        'id': room_id,
        'state': room._state,
        'white_player': room.white_player.__json__() if room.white_player is not None else None,
        'black_player': room.black_player.__json__() if room.black_player is not None else None,
        'viewers': { user_id: viewer.user.__json__() for (user_id, viewer) in room.viewers.items() },
        'user': current_user.__json__()
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
    room = app.room_list[room_id]
    return json.dumps({
            'white_player': room.white_player.__json__(),
            'black_player': room.black_player.__json__(),
            'game': room.get_game()
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
    if room.is_player_set(current_user): return

    room.set_player(copy.copy(current_user))
    socketio.emit('player_set', {
        'id': current_user.id,
        'nickname': current_user.nickname,
        'rating': current_user.rating
    }, to=room)
    print(room.is_ready_to_start(), file=sys.stderr)
    print(room.white_player, file=sys.stderr)
    print(room.black_player, file=sys.stderr)
    if room.is_ready_to_start():
        room.start_game()
        socketio.emit('game_started',
            {
            'white_player': room.white_player.__json__(),
            'black_player': room.black_player.__json__(),
            'game': { 'id': room.get_game()['id'] }
            }, to=room)

@socketio.on('made_move')
def move_handler(room_id, move):
    room = app.room_list[room_id]
    move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
    # если клиент отправит ход от неправильного игрока, там будет None
    if move.is_white_player is not None:
        move = room.handle_move(move)
    emit('made_move', json.dumps({
        'game': room.get_game(),
        'move': move
        }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4), to=room)

@server.route('/user')
def user_route():
    return current_user.id # TODO

@server.route('/user/<int:user_id>')
def user_by_id_route(user_id):
    return current_user.id # TODO