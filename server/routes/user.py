from flask import request, render_template, send_from_directory, redirect, make_response
from flask_login import current_user, login_user, logout_user
from ..database_models import *
from ..forms import LoginForm, RegisterForm
from server import app

server = app
socketio = app.socketio

@server.route('/login', methods=['POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect('/')
    login_form = LoginForm()
    if login_form.login_submit.data and login_form.validate():
        try:
            user = User.login_user(login_form.login_email.data, login_form.login_password.data)
        except LoginError:
            return redirect('/') # TODO: pass an error here
        
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
        try:
            user = User.register_new_user(reg_form.reg_email.data, reg_form.reg_password.data, reg_form.reg_nickname.data)
            login_user(user, remember=True) # TODO: no rem field exists yet
            return redirect('/')
        except RegisterError:
            return redirect('/') # TODO: pass error message here
    return redirect('/')