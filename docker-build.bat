@echo off
echo 🐳 Сборка Docker образа для Yandex Search App...

REM Сборка образа
docker build -t yandex-search-app:latest .

if %errorlevel% equ 0 (
    echo ✅ Образ успешно собран!
    echo.
    echo 🚀 Запуск контейнера...
    
    REM Создаем директорию для экспорта файлов
    if not exist exports mkdir exports
    
    REM Запуск контейнера
    docker run -d ^
        --name yandex-search-app ^
        -p 5000:5000 ^
        -v "%cd%\.env:/app/.env:ro" ^
        -v "%cd%\exports:/app/exports" ^
        --restart unless-stopped ^
        yandex-search-app:latest
    
    if %errorlevel% equ 0 (
        echo ✅ Контейнер успешно запущен!
        echo.
        echo 📱 Приложение доступно по адресу:
        echo    Backend API: http://localhost:5000
        echo    Frontend: http://localhost:3000 (если запущен отдельно)
        echo.
        echo 📊 Полезные команды:
        echo    docker logs yandex-search-app          # Просмотр логов
        echo    docker stop yandex-search-app          # Остановка
        echo    docker start yandex-search-app         # Запуск
        echo    docker rm yandex-search-app            # Удаление
    ) else (
        echo ❌ Ошибка при запуске контейнера!
        exit /b 1
    )
) else (
    echo ❌ Ошибка при сборке образа!
    exit /b 1
)
