from ...database import *
from server import app
from flask import request, render_template, send_from_directory, redirect, make_response, session
from flask_socketio import emit, join_room, leave_room, rooms
from flask_login import current_user
import json

from .game_logic import GameMove
import sys
import copy
from .room import *
# from .room import Room

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