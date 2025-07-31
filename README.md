# 📄 Page Summarizer

AI-приложение для создания кратких резюме веб-страниц с веб-интерфейсом на Flask.

## 🚀 Возможности

- **Автоматическое резюме** веб-страниц с помощью OpenAI GPT-4o
- **Веб-интерфейс** для удобного использования
- **История запросов** с сохранением всех резюме
- **Статистика** использования приложения
- **Логирование** через Logtail
- **Docker** контейнеризация для простого развертывания
- **Автообновление** через cron

## 🛠 Технологии

- **Python 3.11** - основной язык
- **Flask** - веб-фреймворк
- **OpenAI API** - генерация резюме
- **BeautifulSoup** - парсинг HTML
- **Docker** - контейнеризация
- **Logtail** - логирование

## 📦 Установка

### Локальная установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/YOUR_USERNAME/page_summarizer.git
cd page_summarizer
```

2. **Создайте виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установите зависимости**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения**
```bash
cp envExample .env
# Отредактируйте .env файл, добавив ваш API ключ
```

5. **Запустите приложение**
```bash
python app.py
```

### Docker установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/YOUR_USERNAME/page_summarizer.git
cd page_summarizer
```

2. **Настройте переменные окружения**
```bash
cp envExample .env
# Отредактируйте .env файл
```

3. **Запустите с Docker Compose**
```bash
docker-compose up -d
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# OpenAI API Configuration (через proxy)
OPENAI_API_KEY=your_openai_api_key

# Logtail Configuration (для логирования)
LOGTAIL_TOKEN=your_logtail_token

# Optional: Custom timeout for requests (in seconds)
REQUEST_TIMEOUT=10

# Optional: Custom user agent
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## 🌐 Использование

### Веб-интерфейс

1. Откройте браузер и перейдите на `http://localhost:5000`
2. Введите URL страницы для резюме
3. Нажмите "Создать резюме"
4. Просматривайте историю запросов

### API Endpoints

- `GET /` - главная страница
- `POST /summarize` - создание резюме
- `GET /history` - история запросов
- `GET /stats` - статистика
- `GET /health` - проверка здоровья

### Пример API запроса

```bash
curl -X POST http://localhost:5000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## 🐳 Docker команды

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Просмотр логов
```bash
docker-compose logs -f page-summarizer
```

### Пересборка
```bash
docker-compose down
docker-compose up --build -d
```

## 📊 Мониторинг

### Логи
- Локальные логи: `logs/app.log`
- Docker логи: `docker-compose logs page-summarizer`
- Logtail: внешнее логирование

### Статистика
- Количество запросов
- Успешные/неуспешные запросы
- Средняя длина резюме

## 🔄 Автообновление

### Настройка cron
```bash
chmod +x update-setup.sh
./update-setup.sh
```

### Ручное обновление
```bash
chmod +x update-app.sh
./update-app.sh
```

## 🏗 Архитектура

```
page_summarizer/
├── app.py              # Flask приложение
├── agent.py            # Основная логика резюме
├── openai_module.py    # Интеграция с OpenAI
├── history.py          # Управление историей
├── logger_config.py    # Настройка логирования
├── templates/          # HTML шаблоны
├── requirements.txt    # Python зависимости
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose
└── development/        # Файлы для разработки
```

## 🧪 Тестирование

### Запуск тестов
```bash
cd development
python test_agent.py
python test_openai.py
```

### Тестовые данные
- `example.py` - пример использования
- Тестовые URL в тестах

## 🚀 Развертывание на сервере

### 1. Загрузите файлы на сервер
```bash
scp -r page_summarizer/ user@server:/home/user/
```

### 2. Подключитесь к серверу
```bash
ssh user@server
cd page_summarizer
```

### 3. Запустите приложение
```bash
docker-compose up -d
```

### 4. Настройте автообновление
```bash
chmod +x update-setup.sh
./update-setup.sh
```

## 📝 Лицензия

MIT License

## 👥 Авторы

- Разработчик: [Ваше имя]
- Версия: 1.0.0

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/page_summarizer/issues)
- Email: your.email@example.com

---

**Page Summarizer** - умное резюме веб-страниц с помощью AI 🚀 