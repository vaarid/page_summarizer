"""
Модуль для работы с OpenAI API через proxy для создания резюме текста.

Этот модуль содержит функцию для отправки текста в OpenAI API
и получения краткого резюме в 3-5 предложений на русском языке.
Работает с текстами на любом языке, но всегда возвращает резюме на русском.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
SYSTEM_PROMPT = "Ты аналитик. Сформулируй суть текста в 3–5 предложениях на русском языке. Даже если исходный текст на другом языке, всегда отвечай на русском."
MODEL_NAME = "gpt-4o"
PROXY_BASE_URL = "https://api.proxyapi.ru/openai/v1"


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