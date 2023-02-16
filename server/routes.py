from server import app, server
from flask import request
import json


@server.route('/')
@server.route('/index')
def index():
    return '<h1>Hello world</h1>'

@server.route('/login')
def login():
    return '<h1>Login</h1>'

@server.route('/register')
def register():
    return '<h1>Register</h1>'





@server.route('/room', methods=['GET', 'POST'])
def room():
    if request.method == 'GET':
        return json.dumps(app.get_room_list())
        # pass
    elif request.method == 'POST':
        room = Room()
        app.room_list[room.id] = room
        return redirect('room/' + str(room.id))
    else:
        pass

    return '<h1>Room</h1>'

@server.route('/room/<int:room_id>')
def room(room_id):
    if room_id not in app.room_list:
        return redirect('/')
    
    room = app.room_list[room_id]

    if room.player_1 is None:
        room.player_1 = current_user.id
        return room.id # TODO        
    elif room.player_2 is None:
        room.player_2 = current_user.id
        return room.id # TODO
    else:
        pass # TODO

@server.route('/user')
def user():
    return current_user.id # TODO

@server.route('/user/<int:user_id>')
def user(user_id):
    return current_user.id # TODO