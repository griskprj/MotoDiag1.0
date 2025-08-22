from flask import render_template, current_app
from flask_mail import Message
from threading import Thread
from app.extension import mail
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

def send_async_email(app, msg):
    """Асинхронная отправка email"""
    try:
        with app.app_context():
            mail.send(msg)
            app.logger.info(f"Email отправлен на {msg.recipients}")
    except Exception as e:
        app.logger.error(f"Ошибка отправки email: {e}")

def send_email(subject, recipients, template, **kwargs):
    """Основная функция отправки email - немедленный возврат ответа"""
    app = current_app._get_current_object()
    
    try:
        # Рендерим шаблон
        html_content = render_template(template, **kwargs)
        
        # Создаем сообщение
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients
        )
        msg.html = html_content
        
        # Запускаем в отдельном потоке (не блокируем основной запрос)
        thread = Thread(target=send_async_email, args=[app, msg])
        thread.daemon = True  # Поток будет завершен при выходе из основного
        thread.start()
        
        app.logger.info(f"Задача отправки email запущена в фоне для {recipients}")
        return True
        
    except Exception as e:
        app.logger.error(f"Ошибка подготовки email: {e}")
        return False