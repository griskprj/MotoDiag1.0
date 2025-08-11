from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app.extension import db, limiter
from app.models import User

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
        
        login_user(user, remember=remember)
        flash('Вы успешно вошли в систему', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

'''REGISTER'''
@auth_bp.route("/register", methods=['GET', 'POST'])
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
        
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('auth_bp.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка регистрации: {str(e)}', 'danger')
    
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