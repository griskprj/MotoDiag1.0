from flask import render_template, current_app
from flask_mail import Message
from threading import Thread
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from app.extension import mail

def send_email_simple(subject, recipients, template, **kwargs):
    """Упрощенная функция отправки email"""
    try:
        html_content = render_template(template, **kwargs)
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients
        )
        msg.html = html_content
        
        mail.send(msg)
        current_app.logger.info(f"Email отправлен на {recipients}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Ошибка отправки email: {e}")
        return False