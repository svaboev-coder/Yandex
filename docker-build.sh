#!/bin/bash

# Скрипт для сборки и запуска Docker контейнера

echo "🐳 Сборка Docker образа для Yandex Search App..."

# Сборка образа
docker build -t yandex-search-app:latest .

if [ $? -eq 0 ]; then
    echo "✅ Образ успешно собран!"
    echo ""
    echo "🚀 Запуск контейнера..."
    
    # Создаем директорию для экспорта файлов
    mkdir -p exports
    
    # Запуск контейнера
    docker run -d \
        --name yandex-search-app \
        -p 5000:5000 \
        -v $(pwd)/.env:/app/.env:ro \
        -v $(pwd)/exports:/app/exports \
        --restart unless-stopped \
        yandex-search-app:latest
    
    if [ $? -eq 0 ]; then
        echo "✅ Контейнер успешно запущен!"
        echo ""
        echo "📱 Приложение доступно по адресу:"
        echo "   Backend API: http://localhost:5000"
        echo "   Frontend: http://localhost:3000 (если запущен отдельно)"
        echo ""
        echo "📊 Полезные команды:"
        echo "   docker logs yandex-search-app          # Просмотр логов"
        echo "   docker stop yandex-search-app          # Остановка"
        echo "   docker start yandex-search-app         # Запуск"
        echo "   docker rm yandex-search-app            # Удаление"
    else
        echo "❌ Ошибка при запуске контейнера!"
        exit 1
    fi
else
    echo "❌ Ошибка при сборке образа!"
    exit 1
fi
