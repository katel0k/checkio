from ...database import *
from server import app
from flask import request, render_template, redirect, make_response, session
from flask_login import current_user
import json

from .game_logic import GameMove
import sys
import copy
from .room import *
from ...database.services.RoomService import make_new_room

server = app
socketio = app.socketio

@server.route('/room', methods=['GET', 'POST'])
def room_route():
    if request.method == 'GET':
        return json.dumps({
            "room_list": dict(map(
                lambda room_id:
                    (room_id, {
                        "state": app.room_list[room_id]._state,
                        "playersAmount": len(app.room_list[room_id].viewers)
                    }),
                app.room_list
            ))
            })
    elif request.method == 'POST':
        room = Room(make_new_room())
        app.room_list[room.model.id] = room
        # FIXME: 1 - плейсхолдер
        socketio.emit('room_list_updated', (room.model.id, room.model.state, 1), to=app.lobby)
        return redirect(f'room/{room.model.id}/')
    else:
        pass

    return '<h1>Room</h1>'

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
    return json.dumps(RoomDTO(room))
    # return json.dumps({
        # 'id': room_id,
        # 'state': room.model.state,
        # 'white_player': room.white_player.__json__() if room.white_player is not None else None,
        # 'black_player': room.black_player.__json__() if room.black_player is not None else None,
        # 'viewers': { user_id: viewer.user.__json__() for (user_id, viewer) in room.viewers.items() },
        # 'user': current_user.__json__()
    # }, default=lambda o: o.__dict__, 
        # sort_keys=True, indent=4)

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

@server.route('/user')
def user_route():
    return current_user.id # TODO

@server.route('/user/<int:user_id>')
def user_by_id_route(user_id):
    return current_user.id # TODO