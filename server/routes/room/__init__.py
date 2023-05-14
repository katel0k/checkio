from ...database import *
from server import app
from flask import request, render_template, redirect, make_response
from flask_login import current_user
import json

from .room import *
from ...database.services.RoomService import make_new_room

server = app
socketio = app.socketio

@server.route('/room', methods=['GET', 'POST'])
def room_route():
    if request.method == 'GET':
        return json.dumps({
            "room_list": {
                room_id: RoomDTO(room) for (room_id, room) in app.room_list.items()
            }
        })
    elif request.method == 'POST':
        room = Room(make_new_room())
        app.room_list[room.model.id] = room
        socketio.emit('room_list_updated', (room.model.id, RoomDTO(room)), to=app.lobby)
        return redirect(f'room/{room.model.id}/')

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

@server.route('/room/<int:room_id>/game')
def room_id_game_route(room_id):
    if room_id not in app.room_list:
        return make_response('Incorrect room id, no such room exists', 400)
    room = app.room_list[room_id]
    return json.dumps(GameLoopDTO(room.game_loop))