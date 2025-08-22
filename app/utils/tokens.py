from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_confirmation_token(email):
    serializer = current_app.serializer
    return serializer.dumps(email, salt='email-confirmation')

def confirm_token(token, expiration=3000):
    serializer = current_app.serializer
    try:
        email = serializer.loads(
            token,
            salt='email-confirmation',
            max_age=expiration
        )
    except:
        return False
    return email
