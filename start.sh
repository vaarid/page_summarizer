#!/bin/bash
# Скрипт запуска Page Summarizer в Docker

set -e

echo "🚀 Запуск Page Summarizer в Docker"
echo "=================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "📥 Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "📥 Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  ВНИМАНИЕ: Файл .env не найден!"
    echo "📝 Создаю .env файл на основе envExample..."
    cp envExample .env
    echo "✅ Файл .env создан."
    echo "🔧 Отредактируйте .env файл и добавьте API ключи!"
    echo "   - OPENAI_API_KEY=your_key_here"
    echo "   - LOGTAIL_TOKEN=your_token_here (опционально)"
    exit 1
fi

# Создание папок для данных
echo "📁 Создание папок для данных..."
mkdir -p logs data

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true

# Сборка и запуск
echo "🔨 Сборка образа..."
docker-compose build

echo "🚀 Запуск контейнера..."
docker-compose up -d

# Проверка статуса
echo "⏳ Ожидание запуска приложения..."
sleep 10

if docker-compose ps | grep -q "Up"; then
    echo "✅ Приложение успешно запущено!"
    echo "🌐 Доступно по адресу: http://localhost:5000"
    echo ""
    echo "📊 Полезные команды:"
    echo "   • Просмотр логов: docker-compose logs -f"
    echo "   • Остановка: docker-compose down"
    echo "   • Перезапуск: docker-compose restart"
    echo "   • Статус: docker-compose ps"
else
    echo "❌ Ошибка запуска приложения!"
    echo "📋 Логи: docker-compose logs"
    exit 1
fi 