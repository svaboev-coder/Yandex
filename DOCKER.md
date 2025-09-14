# 🐳 Docker Setup для Yandex Search App

## 📋 Требования

- Docker Desktop установлен и запущен
- Файл `.env` с API ключами в корне проекта

## 🚀 Быстрый запуск

### Вариант 1: Использование docker-compose (рекомендуется)

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Вариант 2: Использование скриптов

**Linux/Mac:**
```bash
chmod +x docker-build.sh
./docker-build.sh
```

**Windows:**
```cmd
docker-build.bat
```

### Вариант 3: Ручная сборка

```bash
# Сборка образа
docker build -t yandex-search-app:latest .

# Запуск контейнера
docker run -d \
  --name yandex-search-app \
  -p 5000:5000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/exports:/app/exports \
  yandex-search-app:latest
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
YANDEX_SEARCH__API_KEY=your_yandex_api_key
PROXYAPI_KEY=your_proxy_api_key
PROXYAPI_BASE_URL=your_proxy_api_url
```

### Порты

- **5000** - Backend API (Flask)
- **80** - Frontend (Nginx, если используется)

### Volumes

- `.env` - Переменные окружения (только чтение)
- `exports/` - Директория для экспорта Excel файлов

## 📊 Управление контейнером

```bash
# Просмотр логов
docker logs yandex-search-app

# Остановка
docker stop yandex-search-app

# Запуск
docker start yandex-search-app

# Перезапуск
docker restart yandex-search-app

# Удаление
docker rm yandex-search-app

# Удаление образа
docker rmi yandex-search-app:latest
```

## 🔍 Отладка

```bash
# Вход в контейнер
docker exec -it yandex-search-app bash

# Проверка статуса
docker ps

# Проверка здоровья
curl http://localhost:5000/api/get_status
```

## 📁 Структура проекта в контейнере

```
/app/
├── app.py              # Основное приложение Flask
├── requirements.txt     # Python зависимости
├── frontend/           # Статические файлы фронтенда
│   └── index.html
├── logs/               # Логи приложения
└── exports/            # Экспортированные Excel файлы
```

## 🚨 Устранение проблем

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
docker logs yandex-search-app

# Проверьте, что порт 5000 свободен
netstat -an | grep 5000
```

### Проблема: API ключи не работают

```bash
# Проверьте, что .env файл смонтирован
docker exec yandex-search-app cat /app/.env
```

### Проблема: Файлы не экспортируются

```bash
# Проверьте права доступа к директории exports
ls -la exports/
```

## 🔄 Обновление

```bash
# Остановка текущего контейнера
docker stop yandex-search-app
docker rm yandex-search-app

# Пересборка образа
docker build -t yandex-search-app:latest .

# Запуск нового контейнера
./docker-build.sh
```

## 📈 Мониторинг

```bash
# Использование ресурсов
docker stats yandex-search-app

# Проверка здоровья
docker inspect yandex-search-app | grep Health
```
