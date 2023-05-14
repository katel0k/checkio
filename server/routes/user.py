from flask import redirect
from flask_login import current_user, login_user, logout_user
from .forms import LoginForm, RegisterForm
from server import app
from ..database.services import UserService

server = app
socketio = app.socketio

@server.route('/login', methods=['POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect('/')
    login_form = LoginForm()
    if login_form.login_submit.data and login_form.validate():
        user = UserService.get_user(login_form.login_email.data, login_form.login_password.data)
        login_user(user, remember=login_form.login_rem.data)
        return redirect('/')
    return redirect('/')

@server.route('/logout')
def logout_route ():
	logout_user()
	return redirect('/')

@server.route('/register', methods=['POST'])
def register_route():
    if current_user.is_authenticated:
        return redirect('/')
    reg_form = RegisterForm()
    if reg_form.reg_submit.data and reg_form.validate():
        user = UserService.register_new_user(reg_form.reg_email.data, reg_form.reg_password.data, reg_form.reg_nickname.data)
        login_user(user, remember=True)
        return redirect('/')
    return redirect('/')