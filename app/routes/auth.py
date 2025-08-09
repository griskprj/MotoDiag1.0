from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta
from app.extension import db, mail, limiter
from app.models import User, PendingRegistration, PasswordResetToken
from flask_mail import Message

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

def generate_verification_token(email):
    return current_app.serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_verification_token(token, max_age=3600):
    try:
        email = current_app.serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=max_age
        )
    except:
        return None
    return email

def send_verification_email(email, token):
    verification_url = url_for('auth_bp.verify_email', token=token, _external=True)
    msg = Message('Подтверждение регистрации', recipients=[email])
    msg.body = f'Для завершения регистрации перейдите по ссылке: {verification_url}'
    mail.send(msg)

def send_password_reset_email(email, token):
    reset_url = url_for('auth_bp.reset_password', token=token, _external=True)
    msg = Message('Сброс пароля MotoDiag', recipients=[email])
    msg.body = f'Для сброса пароля перейдите по ссылке: {reset_url}\n\nЕсли вы не запрашивали сброс пароля, проигнорируйте это письмо'
    mail.send(msg)


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
            token = generate_verification_token(email)
            pending_user = PendingRegistration(
                username=username,
                email=email,
                password=generate_password_hash(password),
                verification_token=token,
                token_expiration=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.session.add(pending_user)
            db.session.commit()
            
            send_verification_email(email, token)
            flash('Ссылка для подтверждения отправлена на почту', 'success')
            return redirect(url_for('auth_bp.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка регистрации: {str(e)}', 'danger')
    
    return render_template('auth/register.html')

''' VERIFY EMAIL '''
@auth_bp.route('/verify/<token>')
def verify_email(token):
    try:
        email = verify_verification_token(token)  # Используем единую функцию
        if not email:
            flash('Недействительная или просроченная ссылка', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        pending_user = PendingRegistration.query.filter_by(email=email).first()
        if not pending_user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('auth_bp.register'))
        
        try:
            user = User(
                username=pending_user.username,
                email=pending_user.email,
                password_hash=pending_user.password)
            
            db.session.add(user)
            db.session.delete(pending_user)
            db.session.commit()
            
            flash('Email подтвержден! Теперь вы можете войти', 'success')
            return redirect(url_for('auth_bp.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка активации: {str(e)}', 'danger')
            return redirect(url_for('auth_bp.register'))
    except Exception as e:
        flash('Недействительная или просроченная ссылка', 'danger')
        return redirect(url_for('auth_bp.register'))

''' LOGOUT '''
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth_bp.login'))

''' СТРАНИЦА <ЗАБЫЛИ ПАРОЛЬ>'''
@auth_bp.route("/forgot_password", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            PasswordResetToken.query.filter_by(email=email).delete()

            token = secrets.token_urlsafe(32)

            reset_token = PasswordResetToken(
                email=email,
                token=token,
                token_expiration=datetime.utcnow() + timedelta(hours=1),
                used=False
            )

            db.session.add(reset_token)
            db.session.commit()

            send_password_reset_email(email, token)
        
        flash('Если аккаунт существует, письмо отправлено', 'info')
        return redirect(url_for('auth_bp.login'))

    return render_template('auth/forgot_password.html')

''' СБРОС ПАРОЛЯ '''
@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=reset_record.email).first()
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('auth_bp.forgot_password'))
    
    reset_record = PasswordResetToken.query.filter_by(token=token, used=False).first()
    current_time = datetime.utcnow()

    if not reset_record or reset_record.token_expiration < current_time:
        flash('Недействительная или просроченная ссылка', 'danger')
        return redirect(url_for('auth_bp.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('auth_bp.reset_password', token=token))
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('auth_bp.reset_password', token=token))
        
        user = User.query.filter_by(email=reset_record.email).first()
        if user:
            user.password_hash = generate_password_hash(password)
            reset_record.used = True
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('auth_bp.login'))
    
    return render_template('auth/reset_password.html', token=token)


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