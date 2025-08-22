from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app.extension import db, limiter
from app.models import User
from app.utils.email import send_email_simple
from app.utils.tokens import confirm_token, generate_confirmation_token

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
        
        if not user.is_confirmed:
            flash('Подтвердите ваш email перед входом', 'warning')
        
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
                password_hash=generate_password_hash(password),
                confirmation_token=generate_confirmation_token(email),
                confirmation_sent_at = datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.commit()

            try:
                confirmation_url = url_for(
                    'auth_bp.confirm_email',
                    token=user.confirmation_token,
                    _external=True
                )

                send_email_simple(
                    subject='Подтверждение регистрации - YourMot',
                    recipients=[email],
                    template='emails/confirm_email.html',
                    username=username,
                    confirmation_url=confirmation_url
                )
                flash('Письмо с подтверждением отправлено на вашу почту!', 'success')
                return redirect(url_for('auth_bp.login'))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при регистрации. Повторите попытку позднее', 'danger')

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации. Повторите попытку позднее', 'danger')
    
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

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        if not email:
            flash('Ссылка подтверждения недействительна или устарела', 'danger')
            return redirect(url_for('auth_bp.login'))
        
        user = User.query.filter_by(email=email).first_or_404()

        if user.is_confirmed:
            flash('Аккаунт уже подвтержден', 'info')
            return redirect(url_for('auth_bp.login'))
        
        user.is_confirmed = True
        user.confirmation_token = None
        user.confirmation_sent_at = None
        db.session.commit()

        try:
            send_email_simple(
                subject='Добро пожаловат в YourMot!',
                recipients=[user.email],
                template='emails/welcome.html',
                username=user.username
            )
        except Exception as e:
            current_app.logger.error(f"Ошибка отправки приветственного письма: {e}")
            
        flash('Email успешно подтвержден! Теперь вы можете войти', 'success')
        return redirect(url_for('auth_bp.login'))
    
    except Exception as e:
        current_app.logger.error(f"Ошибка подтверждения email: {e}")
        flash('Ошибка подтверждения email', 'danger')
        return redirect(url_for('auth_bp.login'))

@auth_bp.route('resend_confirmation')
def resend_confirmation():
    if current_user.is_authenticated and not current_user.is_confirmed:
        try:
            current_user.confirmation_token = generate_confirmation_token(current_user.email)
            current_user.confirmation_sent_at = datetime.utcnow()
            
            db.session.commit()

            confirmation_url = url_for(
                'auth_bp.confirm_email',
                token=current_user.confirmation_token,
                _external=True
            )

            send_email_simple(
                subject='Подтверждение регистрации - YourMot',
                recipients=[current_user.email],
                template='emails/confirm_email.html',
                username=current_user.username,
                confirmation_url=confirmation_url
            )
            flash('Письмо с подтверждением отправлено на вашу почту!', 'success')
        
        except Exception as e:
            current_app.logger.error(f"Ошибка подтверждения email: {e}")
            flash('Ошибка подтверждения email', 'danger')
    
    return redirect(url_for('main.index'))
