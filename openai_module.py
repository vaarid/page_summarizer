"""
Модуль для работы с OpenAI API через proxy для создания резюме текста.
"""

import os
import time
import hashlib
import logging
from typing import Optional, Dict, Any
from threading import Lock
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
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BASE_DELAY = int(os.getenv("BASE_DELAY", "2"))

# Rate Limiting настройки
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "8"))
RATE_LIMIT_WINDOW = 60  # секунды

# Кэш настройки
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "200"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 час

# Глобальные переменные для rate limiting и кэширования
request_times = []
cache: Dict[str, Dict[str, Any]] = {}
rate_limit_lock = Lock()
cache_lock = Lock()

def _get_openai_client() -> OpenAI:
    """Создает и возвращает клиент OpenAI с настройками proxy."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
    
    return OpenAI(
        api_key=api_key,
        base_url=PROXY_BASE_URL
    )

def _check_rate_limit() -> None:
    """Проверяет rate limit и ожидает при необходимости."""
    with rate_limit_lock:
        current_time = time.time()
        
        # Удаляем старые запросы
        global request_times
        request_times = [req_time for req_time in request_times 
                        if current_time - req_time < RATE_LIMIT_WINDOW]
        
        # Если достигнут лимит, ждем
        if len(request_times) >= MAX_REQUESTS_PER_MINUTE:
            oldest_request = min(request_times)
            wait_time = RATE_LIMIT_WINDOW - (current_time - oldest_request)
            if wait_time > 0:
                logger.warning(f"Достигнут rate limit. Ожидание {wait_time:.1f} секунд...")
                time.sleep(wait_time)
                current_time = time.time()
        
        # Добавляем текущий запрос
        request_times.append(current_time)

def _get_cache_key(text: str) -> str:
    """Генерирует ключ кэша для текста."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def _get_from_cache(text: str) -> Optional[str]:
    """Получает результат из кэша."""
    with cache_lock:
        key = _get_cache_key(text)
        if key in cache:
            item = cache[key]
            if time.time() - item['timestamp'] < CACHE_TTL:
                logger.info("Результат найден в кэше")
                return item['result']
            else:
                del cache[key]
        return None

def _save_to_cache(text: str, result: str) -> None:
    """Сохраняет результат в кэш."""
    with cache_lock:
        key = _get_cache_key(text)
        
        if len(cache) >= CACHE_MAX_SIZE:
            oldest_key = min(cache.keys(), key=lambda k: cache[k]['timestamp'])
            del cache[oldest_key]
        
        cache[key] = {
            'result': result,
            'timestamp': time.time()
        }
        logger.info("Результат сохранен в кэш")

def summarize_text(text: str) -> str:
    """Создает краткое резюме текста с помощью OpenAI API через proxy."""
    # Проверяем кэш
    cached_result = _get_from_cache(text)
    if cached_result:
        return cached_result
    
    # Проверяем rate limit
    _check_rate_limit()
    
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
            
            result = response.choices[0].message.content.strip()
            
            # Сохраняем в кэш
            _save_to_cache(text, result)
            
            return result
            
        except RateLimitError as e:
            logger.warning(f"Превышен лимит запросов (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                logger.info(f"Ожидание {delay} секунд перед повторной попыткой...")
                time.sleep(delay)
                _check_rate_limit()
            else:
                raise Exception(f"Превышен лимит запросов после {MAX_RETRIES} попыток. Попробуйте позже.")
                
        except APIError as e:
            if "429" in str(e):
                logger.warning(f"Ошибка 429 - Too many requests (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
                
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)
                    logger.info(f"Ожидание {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                    _check_rate_limit()
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