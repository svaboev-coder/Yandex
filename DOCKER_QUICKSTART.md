# 🐳 Быстрый запуск с Docker

## ⚡ Быстрый старт

### 1. Запустите Docker Desktop
- Откройте Docker Desktop на Windows
- Дождитесь полной загрузки (зеленый индикатор)

### 2. Создайте .env файл
Создайте файл `.env` в корне проекта:
```env
YANDEX_SEARCH__API_KEY=ваш_ключ_яндекс
PROXYAPI_KEY=ваш_ключ_proxy
PROXYAPI_BASE_URL=ваш_url_proxy
```

### 3. Запустите приложение

**Вариант A: Через docker-compose (рекомендуется)**
```cmd
docker-compose up -d
```

**Вариант B: Через batch файл**
```cmd
docker-build.bat
```

**Вариант C: Ручная сборка**
```cmd
docker build -t yandex-search-app:latest .
docker run -d --name yandex-search-app -p 5000:5000 -v %cd%\.env:/app/.env:ro yandex-search-app:latest
```

### 4. Проверьте работу
- Backend: http://localhost:5000/api/get_status
- Frontend: http://localhost:3000 (запустите отдельно)

## 🔧 Управление

```cmd
# Просмотр логов
docker logs yandex-search-app

# Остановка
docker stop yandex-search-app

# Запуск
docker start yandex-search-app

# Удаление
docker rm yandex-search-app
```

## 🚨 Если что-то не работает

1. **Docker не запускается**: Запустите Docker Desktop
2. **Ошибка сборки**: Проверьте, что все файлы на месте
3. **API не работает**: Проверьте .env файл
4. **Порт занят**: Остановите другие приложения на порту 5000

## 📱 Доступ к приложению

После успешного запуска:
- **API**: http://localhost:5000
- **Frontend**: Запустите отдельно на порту 3000
- **Статус**: http://localhost:5000/api/get_status
