from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app.extension import db, limiter
from app.models import User
from app.utils.send_email import send_confirmation_email
import os

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

'''LOGIN'''
@auth_bp.route("/login", methods=['POST', 'GET'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember-me') == 'on'
        
        if not username or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('auth_bp.login'))
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Неверные учетные данные', 'danger')
            return redirect(url_for('auth_bp.login'))
        
        if not user.email_confirmed:
            flash('Подтвердите email перед входом', 'danger')
            return redirect(url_for('auth_bp.login'))
        
        login_user(user, remember=True)
        flash('Вы успешно вошли в систему', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

'''REGISTER'''
@auth_bp.route("/register", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Валидация данных
        if not all([username, email, password]):
            flash('Заполните все поля', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        if len(password) < 6:
            flash('Пароль должен быть длиннее 6 символов', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
            )
            
            db.session.add(user)
            db.session.commit()

            send_confirmation_email(user)
            
            flash('Регистрация успешна. Проверьте вашу почту для подтверждения email', 'success')
            return redirect(url_for('auth_bp.login'))
        
        except Exception as e:
            db.session.delete(user)
            db.session.commit()
            db.session.rollback()
            current_app.logger.error(f"Ошибка регистрации: {e}")
            flash('Ошибка при регистрации. Повторите попытку позднее', 'danger')
    
    return render_template('auth/register.html')

''' LOGOUT '''
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route("/user_image/<int:user_id>")
@login_required
def user_image(user_id):
    user = User.query.get_or_404(user_id)

    from io import BytesIO
    from flask import send_file

    if user.image:
        return send_file(
            BytesIO(user.image),
            mimetype='image/jpg',
            as_attachment=False
        )

''' EMAIL CONFIRMATION '''
@auth_bp.route("/confirm/<token>")
@limiter.limit("5 per minute")
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=3600 # 1 hour
        )
    except:
        flash('Ссылка просрочена или недействительна', 'danger')
        return redirect(url_for('auth_bp.login'))
    
    user = User.query.filter_by(email=email).first_or_404()

    if user.email_confirmed:
        flash('Аккаунт уже подтвержден ', 'info')
    else:
        user.email_confirmed = True
        db.session.commit()
        flash('Email успешно подтвержден!', 'success')
    
    return redirect(url_for('main.index'))

''' RESED CONFIRMATION '''
@auth_bp.route("/resend_confirmation")
@limiter.limit("5 per minute")
def resend_confirmation():
    if current_user.email_confirmed:
        flash('Ваш email уже подтвержден', 'info')
        return redirect(url_for('main.index'))
    
    send_confirmation_email(current_user)
    flash('Новое письмо с подтверждением отправлено на ваш email', 'info')
    return redirect(url_for('main.index'))
