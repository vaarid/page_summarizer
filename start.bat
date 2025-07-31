@echo off
REM Скрипт запуска Page Summarizer в Docker для Windows

echo 🚀 Запуск Page Summarizer в Docker
echo ==================================

REM Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен!
    echo 📥 Установите Docker: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен!
    echo 📥 Установите Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Проверяем наличие .env файла
if not exist ".env" (
    echo ⚠️  ВНИМАНИЕ: Файл .env не найден!
    echo 📝 Создаю .env файл на основе envExample...
    copy envExample .env
    echo ✅ Файл .env создан.
    echo 🔧 Отредактируйте .env файл и добавьте API ключи!
    echo    - OPENAI_API_KEY=your_key_here
    echo    - LOGTAIL_TOKEN=your_token_here (опционально)
    pause
    exit /b 1
)

REM Создание папок для данных
echo 📁 Создание папок для данных...
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Остановка существующих контейнеров
echo 🛑 Остановка существующих контейнеров...
docker-compose down >nul 2>&1

REM Сборка и запуск
echo 🔨 Сборка образа...
docker-compose build

echo 🚀 Запуск контейнера...
docker-compose up -d

REM Проверка статуса
echo ⏳ Ожидание запуска приложения...
timeout /t 10 /nobreak >nul

docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Ошибка запуска приложения!
    echo 📋 Логи: docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Приложение успешно запущено!
    echo 🌐 Доступно по адресу: http://localhost:5000
    echo.
    echo 📊 Полезные команды:
    echo    • Просмотр логов: docker-compose logs -f
    echo    • Остановка: docker-compose down
    echo    • Перезапуск: docker-compose restart
    echo    • Статус: docker-compose ps
)

pause 