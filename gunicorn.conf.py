# gunicorn.conf.py
workers = 2
worker_class = 'sync'
timeout = 30  # Увеличьте до 30 секунд
keepalive = 2
bind = 'unix:motodiag.sock'
preload_app = True  # Предзагрузка приложения