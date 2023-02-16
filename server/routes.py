from server import app, server
from flask import request
import json


@server.route('/')
@server.route('/index')
def index_route():
    return '<h1>Hello world</h1>'

@server.route('/login')
def login_route():
    return '<h1>Login</h1>'

@server.route('/register')
def register_route():
    return '<h1>Register</h1>'





@server.route('/room', methods=['GET', 'POST'])
def room_route():
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
def room_id_route(room_id):
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
def user_route():
    return current_user.id # TODO

@server.route('/user/<int:user_id>')
def user_by_id_route(user_id):
    return current_user.id # TODO