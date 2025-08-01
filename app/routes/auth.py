from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('auth_bp.login'))
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')
            return redirect(url_for('auth_bp.register'))

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.verify_password(form.password.data):
                login_user(user)
                flash('Вы успешно вошли!', 'success')
                return redirect(url_for('main_bp.dashboard'))
            flash('Неверный email или пароль', 'danger')
        except Exception as e:
            flash (f'Ошибка при входе: {str(e)}', 'danger')
            return redirect(url_for('auth_bp.login'))
        
        return render_template('login.html', form=form)
