# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY backend/ .

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Открываем порт 5000
EXPOSE 5000

# Устанавливаем переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=4
ENV GUNICORN_TIMEOUT=120

# Создаем пользователя для безопасности
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Команда запуска с Gunicorn (production сервер)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
