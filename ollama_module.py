"""
Модуль для работы с Ollama API как альтернативным провайдером для создания резюме текста.

Этот модуль содержит функцию для отправки текста в Ollama API
и получения краткого резюме в 3-5 предложений на русском языке.
Используется как fallback при недоступности основного OpenAI API.
"""

import os
import time
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
SYSTEM_PROMPT = "Ты аналитик. Сформулируй суть текста в 3–5 предложениях на русском языке. Даже если исходный текст на другом языке, всегда отвечай на русском."
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BASE_DELAY = int(os.getenv("BASE_DELAY", "1"))  # секунды


def _get_ollama_url() -> str:
    """
    Получает URL для Ollama API.
    
    Returns:
        URL для Ollama API
        
    Raises:
        ValueError: Если OLLAMA_BASE_URL не настроен
    """
    base_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
    return f"{base_url}/api/generate"


def _check_ollama_available() -> bool:
    """
    Проверяет доступность Ollama сервиса.
    
    Returns:
        True если Ollama доступен, False в противном случае
    """
    try:
        url = _get_ollama_url()
        response = requests.get(url.replace("/api/generate", "/api/tags"), timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama недоступен: {e}")
        return False


def summarize_text(text: str) -> str:
    """
    Создает краткое резюме текста с помощью Ollama API.
    
    Args:
        text: Текст для анализа и создания резюме (может быть на любом языке)
        
    Returns:
        Краткое резюме текста в 3-5 предложений на русском языке
        
    Raises:
        Exception: При ошибках API или недоступности сервиса
    """
    if not _check_ollama_available():
        raise Exception("Ollama сервис недоступен. Убедитесь, что Ollama запущен.")
    
    url = _get_ollama_url()
    
    prompt = f"{SYSTEM_PROMPT}\n\nТекст для анализа:\n{text}"
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Попытка {attempt + 1}/{MAX_RETRIES} создания резюме через Ollama")
            
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "response" in result:
                return result["response"].strip()
            else:
                raise Exception("Неожиданный формат ответа от Ollama")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Ollama (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                logger.info(f"Ожидание {delay} секунд перед повторной попыткой...")
                time.sleep(delay)
            else:
                raise Exception(f"Ошибка запроса к Ollama после {MAX_RETRIES} попыток: {e}")
                
        except Exception as e:
            logger.error(f"Неожиданная ошибка Ollama (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Неожиданная ошибка Ollama после {MAX_RETRIES} попыток: {e}")
            
            delay = BASE_DELAY * (2 ** attempt)
            time.sleep(delay) 