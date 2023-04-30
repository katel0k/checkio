from flask import render_template, request, redirect
from flask_login import current_user
from flask_socketio import join_room

from ..database_models import RoomModel
import json
from ..forms import LoginForm, RegisterForm
from server import app
import random

server = app
socketio = app.socketio

app.lobby = 'lobby'

@server.route('/', methods=['GET', 'POST'])
def index_route():
    login_form = LoginForm()
    reg_form = RegisterForm()
    return render_template('index.html', title="Main page", login_form=login_form, reg_form=reg_form)

@socketio.on('user_joined_lobby')
def user_joined_lobby_event_handler():
    join_room(app.lobby)

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
        room = RoomModel.make_new_room()
        app.room_list[room.id] = room
        socketio.emit('room_list_updated', (room.id, room._state, len(room.viewers)), to=app.lobby)
        return redirect(f'room/{room.id}/')
    else:
        pass

    return '<h1>Room</h1>'

@server.route('/room/random')
def room_random():
    return redirect('/room/' + str(random.choice(list(app.room_list.keys()))))