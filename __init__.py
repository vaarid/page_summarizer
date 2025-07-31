"""
Пакет page_summarizer для создания кратких резюме веб-страниц.

Этот пакет содержит модули для загрузки HTML-контента,
его обработки и создания кратких резюме с помощью OpenAI.
"""

from .agent import summarize_url

__version__ = "1.0.0"
__author__ = "Page Summarizer Team"

__all__ = ["summarize_url"] 