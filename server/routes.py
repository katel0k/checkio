from server import app, server, login_manager
from flask import request, render_template, send_from_directory, redirect
from flask_login import current_user
import json
from forms import LoginForm, RegisterForm


@server.route('/')
@server.route('/index')
def index_route():
    return render_template('index.html', title="Main page")

@server.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # TODO: check database for user existance
        
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is None or not user.check_password(form.password.data):
        # 	return redirect(url_for('login'))
        login_user(user, remember=form.rem.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form, title='Login')

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

@server.route('/room/<int:room_id>')
def room_id_route(room_id):
    return render_template('room.html', title="Game")
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

@server.route('/<path:path>')
@server.route('/room/<path:path>')
def get_file(path):
    return send_from_directory('static', path)