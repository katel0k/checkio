from server import app, server, login_manager, socketio, game_engine
from flask import request, render_template, send_from_directory, redirect, make_response
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user
import json
from forms import LoginForm, RegisterForm
from models import *
import random
from game_logic import Game, GameMove
from setup_db import conn, cur

@server.route('/')
@server.route('/index')
def index_route():
    return render_template('v2/index.html', title="Main page")

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
        # pass
    elif request.method == 'POST':
        room = Room.make_new_room()
        # room = Room()
        app.room_list[room.id] = room
        return redirect('room/' + str(room.id))
    else:
        pass

    return '<h1>Room</h1>'

@server.route('/room/random')
def room_random():
    return redirect('/room/' + str(random.choice(list(app.room_list.keys()))))

@server.route('/room/<int:room_id>')
def room_id_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')

    if not current_user.is_authenticated:
        return redirect('/login')
    
    # room = app.room_list[room_id]

    if request.method != 'GET':
        return redirect('/')

    return render_template('room.html', title="Game", room_id=room_id)

    # if room.player1 is None:
    #     # connect first player
    #     room.player1 = current_user.id
    #     # join_room(room_id)
    #     # emit('joined', namespace="/room")
    #     # TODO: render template with user info
    #     return render_template('room.html', title="Game", room_id=room_id)
    # elif room.player2 is None: # bug: it tries to connect to it after reloading tha page
    #     # connect second player
    #     # emit event for the first one that the second player connected and the game starts
    #     room.player2 = current_user.id
    #     # join_room(room_id)
    #     # emit('both_players_joined', current_user.id, to=room_id)
    #     # render template with both users info
    #     # start the game

    #     return render_template('room.html', title="Game")
    # else:
    #     # this view assumes that the game has already started

    #     # TODO:
    #     # add spectator
    #     # add render for both players

    #     return render_template('room.html', title="Game", game=room.game) # TODO

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
        
# @server.route('/room/<int:room_id>/play')
# def room_id_play_route(room_id):
#     if room_id not in app.room_list:
#         return redirect('/')

#     if not current_user.is_authenticated:
#         return redirect('/login')
    
#     room = app.room_list[room_id]

#     if room.player1 is None or room.player2 is None:
#         return redirect('/')
    
#     room.game = Game()

#     return redirect('/room/' + str(room_id))

@server.route('/room/<int:room_id>/game')
def room_id_info_route(room_id):
    if room_id not in app.room_list:
        return make_response('Incorrect room id, no such room exists', 400)
    room = app.room_list[room_id]
    return json.dumps({
        'field': None if room.game is None else room.game.field,
        'order': room.game.order_color,
        # 'field'json.dumps(self)
        'player1': room.player1, # TODO: make db call here
        'player2': room.player2,
        'player_color': current_user.get_id() == room.player1
    }, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


@socketio.on('join')
def join_event_handler(room_id):
    room = app.room_list[room_id]
    room.add_viewer(current_user)
    join_room(room)
    # if room.player1 is None:
    #     room.player1 = current_user.get_id()
    #     join_room(room)
    # elif room.player2 is None:
    #     room.player2 = current_user.get_id()
    #     room.game = Game()
    #     join_room(room)
    #     emit('both_players_joined', to=room)
        
@socketio.on('made_move')
def move_handler(room_id, move):
    room = app.room_list[room_id]
    move = GameMove((move['y0'], move['x0']), (move['y'], move['x']), move['player_color'])
    game_engine.handle_move(room.game, move) # return value is not needed?
    emit('made_move', json.dumps({
        'field': room.game.field, 'move': move
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