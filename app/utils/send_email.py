from flask import current_app, url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app.extension import mail

def send_confirmation_email(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(
        user.email,
        salt=current_app.config['SECURITY_PASSWORD_SALT']
    )

    confirm_url = url_for('auth_bp.confirm_email', token=token, _external=True)

    html = render_template(
        'emails/confirm_email.html',
        username=user.username,
        confirmation_url=confirm_url
    )

    msg = Message(
        'Подтверждение регистрации - YourMot',
        recipients=[user.email],
        html=html
    )

    mail.send(msg)
