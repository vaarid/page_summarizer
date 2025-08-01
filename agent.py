"""
Модуль агента для создания краткого резюме веб-страниц.

Этот модуль содержит функции для загрузки HTML-контента с URL,
его очистки и передачи в модуль OpenAI для создания резюме.
"""

import logging
import requests
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag

from openai_module import summarize_text
from ollama_module import summarize_text as ollama_summarize_text

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы
MAX_TEXT_LENGTH = 5000
DEFAULT_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def fetch_url_content(url: str) -> Optional[str]:
    """
    Загружает HTML-контент с указанного URL.
    
    Args:
        url: URL страницы для загрузки
        
    Returns:
        HTML-контент в виде строки или None в случае ошибки
        
    Raises:
        requests.exceptions.RequestException: При ошибках сети
        ValueError: При невалидном URL
    """
    try:
        # Валидация URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Невалидный URL: {url}")
        
        logger.info(f"Загружаю контент с URL: {url}")
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Проверяем, что получили HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            logger.warning(f"Получен не HTML контент: {content_type}")
            
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке URL {url}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Ошибка валидации URL {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке {url}: {e}")
        raise


def clean_html(html: str) -> str:
    """
    Извлекает чистый текст из HTML, удаляя теги, скрипты и стили.
    
    Args:
        html: HTML-контент в виде строки
        
    Returns:
        Очищенный текст без HTML-тегов
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Получаем текст
        text = soup.get_text()
        
        # Очищаем от лишних пробелов и переносов строк
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        logger.error(f"Ошибка при очистке HTML: {e}")
        raise


def truncate_text(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    """
    Обрезает текст до указанной длины, сохраняя целостность предложений.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина текста
        
    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    
    # Обрезаем до max_length символов
    truncated = text[:max_length]
    
    # Ищем последнее полное предложение
    last_sentence_end = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence_end > max_length * 0.8:  # Если нашли предложение в последних 20%
        return truncated[:last_sentence_end + 1]
    
    return truncated


def summarize_url(url: str) -> str:
    """
    Создает краткое резюме веб-страницы по URL.
    
    Args:
        url: URL страницы для анализа
        
    Returns:
        Краткое резюме страницы (3-5 предложений)
        
    Raises:
        requests.exceptions.RequestException: При ошибках загрузки
        ValueError: При невалидном URL или пустом контенте
        Exception: При других ошибках обработки
    """
    try:
        # Загружаем HTML-контент
        html_content = fetch_url_content(url)
        if not html_content:
            raise ValueError("Не удалось загрузить контент с указанного URL")
        
        # Очищаем HTML
        clean_text = clean_html(html_content)
        if not clean_text.strip():
            raise ValueError("Не удалось извлечь текстовый контент из HTML")
        
        # Обрезаем текст если он слишком длинный
        if len(clean_text) > MAX_TEXT_LENGTH:
            logger.info(f"Текст слишком длинный ({len(clean_text)} символов), обрезаю до {MAX_TEXT_LENGTH}")
            clean_text = truncate_text(clean_text)
        
        logger.info(f"Подготавливаю резюме для текста длиной {len(clean_text)} символов")
        
        # Создаем резюме через OpenAI модуль с fallback на Ollama
        try:
            summary = summarize_text(clean_text)
            logger.info("Резюме успешно создано через OpenAI API")
        except Exception as e:
            logger.warning(f"Ошибка OpenAI API: {e}. Пробую Ollama...")
            try:
                summary = ollama_summarize_text(clean_text)
                logger.info("Резюме успешно создано через Ollama")
            except Exception as ollama_error:
                logger.error(f"Ошибка Ollama API: {ollama_error}")
                raise Exception(f"Не удалось создать резюме ни через OpenAI, ни через Ollama. OpenAI ошибка: {e}, Ollama ошибка: {ollama_error}")
        
        return summary
        
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Ошибка при обработке URL {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании резюме для {url}: {e}")
        raise 