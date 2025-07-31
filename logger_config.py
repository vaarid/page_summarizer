"""
Модуль для настройки логирования с интеграцией Logtail.

Настраивает логирование для приложения с поддержкой
локального логирования и отправки в Logtail.
"""

import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получение токена Logtail
LOGTAIL_TOKEN = os.getenv('LOGTAIL_TOKEN')


def setup_logging():
    """Настраивает логирование с интеграцией Logtail."""
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Очищаем существующие хендлеры
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Хендлер для файла
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Хендлер для Logtail (если токен указан)
    if LOGTAIL_TOKEN:
        try:
            from logtail import LogtailHandler
            logtail_handler = LogtailHandler(LOGTAIL_TOKEN)
            logtail_handler.setFormatter(formatter)
            logtail_handler.setLevel(logging.INFO)
            root_logger.addHandler(logtail_handler)
            
            root_logger.info('Logtail интеграция активирована')
            print("✅ Logtail подключен успешно!")
            
        except ImportError:
            root_logger.warning('Модуль logtail-python не установлен')
            print("⚠️ Установите logtail-python: pip install logtail-python")
            
        except Exception as e:
            root_logger.warning(f'Не удалось подключить Logtail: {e}')
            print(f"❌ Ошибка подключения к Logtail: {e}")
    else:
        root_logger.info('LOGTAIL_TOKEN не указан, внешнее логирование отключено')
        print("ℹ️ LOGTAIL_TOKEN не найден, логирование только локальное")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Получает логгер с указанным именем."""
    return logging.getLogger(name)


# Инициализируем логирование при импорте модуля
setup_logging()