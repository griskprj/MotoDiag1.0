from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app.extensions import db

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
            return jsonify({'success': True})
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')
            return jsonify({'success': False, 'errors': form.errors}), 400

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return jsonify({
                'success': True,
                'redirect': url_for('main_bp.main')
            })
        return jsonify({
            'success': False,
            'errors': {field.name: field.errors[0] for field in form if field.errors},
            'message': 'Неверные учетные данные'
        }), 400

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('auth_bp.login'))
