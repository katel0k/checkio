from flask import render_template
from flask_login import current_user

from ..forms import LoginForm, RegisterForm
from server import app

server = app
socketio = app.socketio

@server.route('/', methods=['GET', 'POST'])
def index_route():
    login_form = LoginForm()
    reg_form = RegisterForm()
    return render_template('index.html', title="Main page", login_form=login_form, reg_form=reg_form)
