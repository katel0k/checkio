from server import app, server, login_manager, Room, socketio
from flask import request, render_template, send_from_directory, redirect
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user, login_user, logout_user
import json
from forms import LoginForm, RegisterForm
from models import User
import random

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
        # TODO: check database for user existance
        
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is None or not user.check_password(form.password.data):
        # 	return redirect(url_for('login'))
        user = User(1)
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
        # TODO: add user to database


        # user = User(FIO=form.get_FIO(),
        # 		email=form.email.data,
        # 		avatar_src="unauthorized.jpg",
        # 		money=10000,
        # 		rating=2000)
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        return redirect('/login')
    return render_template('register.html', form=form, title='Registration')


@login_manager.user_loader
def load_user(id):
    return User(id)


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

@server.route('/room/random')
def room_random():
    return redirect('/room/' + random.choice(app.room_list.keys()))

@server.route('/room/<int:room_id>')
def room_id_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')

    if not current_user.is_authenticated:
        return redirect('/login')
    
    room = app.room_list[room_id]

    if request.method != 'GET':
        return redirect('/')

    if room.player_1 is None:
        # connect first player
        room.player_1 = current_user.id
        join_room(room_id)
        # TODO: render template with user info
        return render_template('room.html', title="Game")
    elif room.player_2 is None:
        # connect second player
        # emit event for the first one that the second player connected and the game starts
        room.player_2 = current_user.id
        join_room(room_id)
        emit('both_players_joined', current_user.id, to=room_id)
        # render template with both users info
        # start the game

        return render_template('room.hmtl', title="Game")
    else:
        # this view assumes that the game has already started

        # TODO:
        # add spectator
        # add render for both players

        return render_template('room.html', title="Game", game=room.game) # TODO

@server.route('/room/<int:room_id>/leave')
def room_id_leave_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')

    if not current_user.is_authenticated:
        return redirect('/login')
    
    room = app.room_list[room_id]

    if room.player_1 == current_user.id:
        room.player_1, room.player_2 = room.player_2, None
        emit('player_left', to=room)
        # TODO
    elif room.player_2 == current_user.id:
        room.player_2 = None
        emit('player_left', to=room)
        # TODO

    return redirect('/')
        
@server.route('/room/<int:room_id>/agree')
def room_id_agree_route(room_id):
    if room_id not in app.room_list:
        return redirect('/')

    if not current_user.is_authenticated:
        return redirect('/login')
    
    room = app.room_list[room_id]

    if room.player_1 is None or room.player_2 is None:
        return redirect('/')
    
    room.game = Game()

    return redirect('/room/' + str(room_id))


@socketio.on('join', namespace="/room")
def join_event_handler(sid):

    join_room()


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