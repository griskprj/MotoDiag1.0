from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Логин должен быть от 4 до 20 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Некорректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8, message='Пароль должен быть не менее 8 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли не совпадают')
    ])
    privacy = BooleanField('Я согласен с политикой', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
