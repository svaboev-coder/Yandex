# Конфигурация Gunicorn для production

import os
import multiprocessing

# Базовые настройки
bind = "0.0.0.0:5000"
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))
keepalive = 2

# Ограничения для стабильности
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Логирование
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Безопасность
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Производительность
worker_tmp_dir = "/dev/shm"

# Перезапуск воркеров
max_worker_memory = 200  # MB
max_worker_memory_jitter = 50  # MB

# Graceful shutdown
graceful_timeout = 30
