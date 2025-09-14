# 🏗️ Архитектура приложения

## 📋 **Обзор архитектуры:**

Приложение использует **микросервисную архитектуру** с раздельными контейнерами:

### **🔧 Компоненты:**

1. **Backend API** - Flask + Gunicorn
2. **Frontend** - Nginx с статическими файлами
3. **Network** - Docker bridge network

## 🐳 **Docker контейнеры:**

### **Backend контейнер:**
- **Образ**: `yandex-search-backend`
- **Порт**: 5000 (внутренний)
- **Сервис**: Flask API + Gunicorn
- **Функции**:
  - Поиск организаций через Яндекс API
  - Поиск email адресов
  - Экспорт в Excel
  - Управление процессами

### **Frontend контейнер:**
- **Образ**: `yandex-search-frontend`
- **Порт**: 80 (внешний)
- **Сервис**: Nginx
- **Функции**:
  - Отдача статических файлов (HTML, CSS, JS)
  - Reverse proxy для API запросов
  - Маршрутизация запросов

## 🌐 **Сетевая архитектура:**

```
Internet → Frontend (Nginx:80) → Backend (Flask:5000)
```

### **Поток запросов:**
1. **Пользователь** → `http://localhost:80`
2. **Nginx** → отдает статические файлы
3. **API запросы** → `http://localhost:80/api/*`
4. **Nginx** → проксирует на `backend:5000`
5. **Backend** → обрабатывает запрос
6. **Ответ** → возвращается через Nginx

## 📁 **Структура файлов:**

```
project/
├── Dockerfile                 # Backend образ
├── docker-compose.yml         # Оркестрация сервисов
├── backend/
│   ├── Dockerfile            # (не используется)
│   ├── app.py                # Flask приложение
│   ├── requirements.txt      # Python зависимости
│   └── gunicorn.conf.py      # Конфигурация Gunicorn
├── frontend/
│   ├── Dockerfile            # Frontend образ
│   └── index.html            # Статические файлы
└── exports/                  # Экспортированные файлы
```

## 🚀 **Команды запуска:**

### **Полная система:**
```bash
docker-compose up -d
```

### **Только backend:**
```bash
docker-compose up -d backend
```

### **Только frontend:**
```bash
docker-compose up -d frontend
```

## 🔍 **Проверка работы:**

### **Backend API:**
```bash
# Прямой доступ к API (внутренний)
docker exec yandex-search-backend curl http://localhost:5000/api/get_status

# Через frontend (внешний)
curl http://localhost:80/api/get_status
```

### **Frontend:**
```bash
# Статические файлы
curl http://localhost:80

# Health check
docker exec yandex-search-frontend curl http://localhost:80
```

## 📊 **Преимущества архитектуры:**

### **✅ Разделение ответственности:**
- **Backend** - только API логика
- **Frontend** - только статические файлы
- **Nginx** - только маршрутизация

### **✅ Масштабируемость:**
- Можно масштабировать backend независимо
- Можно добавить несколько backend инстансов
- Можно использовать CDN для frontend

### **✅ Безопасность:**
- Backend не доступен извне напрямую
- Nginx как reverse proxy
- Изоляция сервисов

### **✅ Развертывание:**
- Независимое обновление компонентов
- Отдельные образы для каждого сервиса
- Простое масштабирование

## 🔧 **Конфигурация Nginx:**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    # Статические файлы
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API запросы
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🎯 **Доступ к приложению:**

- **Frontend**: http://localhost:80
- **API**: http://localhost:80/api/*
- **Статус**: http://localhost:80/api/get_status

## 🔄 **Обновление компонентов:**

### **Обновление backend:**
```bash
docker-compose build backend
docker-compose up -d backend
```

### **Обновление frontend:**
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### **Полное обновление:**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 📈 **Мониторинг:**

```bash
# Статус всех сервисов
docker-compose ps

# Логи backend
docker-compose logs backend

# Логи frontend
docker-compose logs frontend

# Использование ресурсов
docker stats
```

**Эта архитектура обеспечивает максимальную гибкость, безопасность и масштабируемость!** 🎉
