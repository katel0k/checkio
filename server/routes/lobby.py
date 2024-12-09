from flask import render_template, redirect
from flask_socketio import join_room

from .forms import LoginForm, RegisterForm
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

@server.route('/room/random')
def room_random():
    return redirect('/room/' + str(random.choice(list(app.room_list.keys()))))
