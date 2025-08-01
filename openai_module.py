"""
Модуль для работы с OpenAI API через proxy для создания резюме текста.

Этот модуль содержит функцию для отправки текста в OpenAI API
и получения краткого резюме в 3-5 предложений на русском языке.
Работает с текстами на любом языке, но всегда возвращает резюме на русском.
"""

import os
import time
import logging
from typing import Optional
from openai import OpenAI
from openai import RateLimitError, APIError
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
SYSTEM_PROMPT = "Ты аналитик. Сформулируй суть текста в 3–5 предложениях на русском языке. Даже если исходный текст на другом языке, всегда отвечай на русском."
MODEL_NAME = "gpt-4o"
PROXY_BASE_URL = "https://api.proxyapi.ru/openai/v1"
MAX_RETRIES = 3
BASE_DELAY = 2  # секунды


def _get_openai_client() -> OpenAI:
    """
    Создает и возвращает клиент OpenAI с настройками proxy.
    
    Returns:
        OpenAI клиент с настроенным base_url
        
    Raises:
        ValueError: Если OPENAI_API_KEY не найден в переменных окружения
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
    
    return OpenAI(
        api_key=api_key,
        base_url=PROXY_BASE_URL
    )


def summarize_text(text: str) -> str:
    """
    Создает краткое резюме текста с помощью OpenAI API через proxy.
    
    Args:
        text: Текст для анализа и создания резюме (может быть на любом языке)
        
    Returns:
        Краткое резюме текста в 3-5 предложений на русском языке
        
    Raises:
        ValueError: При отсутствии API ключа
        Exception: При ошибках API или сети
    """
    client = _get_openai_client()
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Попытка {attempt + 1}/{MAX_RETRIES} создания резюме")
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except RateLimitError as e:
            logger.warning(f"Превышен лимит запросов (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)  # Экспоненциальная задержка
                logger.info(f"Ожидание {delay} секунд перед повторной попыткой...")
                time.sleep(delay)
            else:
                raise Exception(f"Превышен лимит запросов после {MAX_RETRIES} попыток. Попробуйте позже.")
                
        except APIError as e:
            if "429" in str(e):
                logger.warning(f"Ошибка 429 - Too many requests (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
                
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)  # Экспоненциальная задержка
                    logger.info(f"Ожидание {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Превышен лимит запросов после {MAX_RETRIES} попыток. Попробуйте позже.")
            else:
                logger.error(f"Ошибка API (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Ошибка API после {MAX_RETRIES} попыток: {e}")
                time.sleep(BASE_DELAY)
                
        except Exception as e:
            logger.error(f"Неожиданная ошибка (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Неожиданная ошибка после {MAX_RETRIES} попыток: {e}")
            time.sleep(BASE_DELAY) 