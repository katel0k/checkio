from server import app, server, login_manager, socketio
from flask import request, render_template, send_from_directory, redirect, make_response
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user
import json
from forms import LoginForm, RegisterForm
from models import *
import random
from game_logic import Game, GameMove
from setup_db import conn, cur
import sys

@server.route('/')
@server.route('/index')
def index_route():
    return render_template('index.html', title="Main page")

@server.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.login_user(form.email.data, form.password.data)
        except LoginError:
            return redirect('/login') # TODO: pass an error here
        
        login_user(user, remember=form.rem.data)
        return redirect('/')
    return render_template('login.html', form=form, title='Login')

@server.route('/logout')
def logout_route ():
	logout_user()
	return redirect('/')

@server.route('/register', methods=['GET', 'POST'])
def register_route():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register_new_user(form.email.data, form.password.data, form.nickname.data)
            login_user(user, remember=True) # TODO: no rem field exists yet
            return redirect('/')
        except RegisterError:
            return redirect('/register') # TODO: pass error message here
    return render_template('register.html', form=form, title='Registration')


@server.route('/room', methods=['GET', 'POST'])
def room_route():
    if request.method == 'GET':
        return json.dumps({
            "room_list": list(app.get_room_list().keys())
            })
    elif request.method == 'POST':
        room = Room.make_new_room()
        app.room_list[room.id] = room
        return redirect(f'room/{room.id}/')
    else:
        pass

    return '<h1>Room</h1>'

@server.route('/room/random')
def room_random():
    return redirect('/room/' + str(random.choice(list(app.room_list.keys()))))

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
    return json.dumps({
        'id': room_id,
        'state': app.room_list[room_id]._state
        })

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
    # print(current_user.get_id(), file=sys.stderr)
    # print(room._game_setter.game.white_player, file=sys.stderr)
    return json.dumps({
        'field': game_obj.game.field,
        'order': game_obj.game.is_white_move,
        'white_player': game_obj.white_player.user_id,
        'white_player': game_obj.black_player.user_id,
        'player_color': current_user.get_id() == game_obj.white_player.user_id
    }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


@socketio.on('join')
def join_event_handler(room_id):
    # print(room_id, file=sys.stderr)
    room = app.room_list[room_id]
    room.add_viewer(current_user)
    join_room(room)
        



@socketio.on('join_game')
def join_game_event_handler(room_id):
    room = app.room_list[room_id]
    room.set_player(current_user.get_id())
    if room.is_ready_to_start():
        room.start_game()
        # room._game_setter.game
        socketio.emit('ready_to_start', to=room)

@socketio.on('made_move')
def move_handler(room_id, move):
    room = app.room_list[room_id]
    move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
    # game_engine.handle_move(room._game_setter.game.game, move)
    room._game_setter.game.game.handle_move(move)
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