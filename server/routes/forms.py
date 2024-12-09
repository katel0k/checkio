from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, EqualTo

class LoginForm(FlaskForm):
	login_email = StringField('Email', validators=[DataRequired(message='no email'), Email(message='email error')])
	login_password = PasswordField('Password', validators=[DataRequired(message='no password')])
	login_rem = BooleanField('Remember Me')
	login_submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
	reg_email = StringField('Email', validators=[DataRequired(), Email()])
	reg_password = PasswordField('Password', validators=[DataRequired()])
	reg_password2 = PasswordField('Password repeat', validators=[DataRequired(), EqualTo('reg_password')])
	reg_nickname = StringField('Nickname', validators=[DataRequired()])
	reg_submit = SubmitField('Sign Up')
