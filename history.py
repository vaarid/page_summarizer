"""
Модуль для управления историей запросов.

Сохраняет историю запросов локально в JSON файле
и предоставляет функции для работы с ней.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Константы
HISTORY_FILE = "request_history.json"
MAX_HISTORY_SIZE = 100  # Максимальное количество записей в истории


class HistoryManager:
    """Менеджер для работы с историей запросов."""
    
    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Создает файл истории, если он не существует."""
        if not os.path.exists(self.history_file):
            self._save_history([])
            logger.info(f"Создан новый файл истории: {self.history_file}")
    
    def _load_history(self) -> List[Dict]:
        """Загружает историю из файла."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history if isinstance(history, list) else []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Ошибка загрузки истории: {e}")
            return []
    
    def _save_history(self, history: List[Dict]):
        """Сохраняет историю в файл."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения истории: {e}")
    
    def add_request(self, url: str, summary: str, success: bool = True, error: Optional[str] = None) -> Dict:
        """Добавляет новый запрос в историю."""
        history = self._load_history()
        
        # Создаем новую запись
        record = {
            'id': len(history) + 1,
            'url': url,
            'summary': summary if success else None,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'char_count': len(summary) if success and summary else 0,
            'sentence_count': len(summary.split('.')) if success and summary else 0
        }
        
        # Добавляем в начало списка
        history.insert(0, record)
        
        # Ограничиваем размер истории
        if len(history) > MAX_HISTORY_SIZE:
            history = history[:MAX_HISTORY_SIZE]
        
        # Обновляем ID
        for i, record in enumerate(history):
            record['id'] = i + 1
        
        self._save_history(history)
        logger.info(f"Добавлен запрос в историю: {url}")
        
        return record
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Получает историю запросов."""
        history = self._load_history()
        if limit:
            history = history[:limit]
        return history
    
    def get_request_by_id(self, request_id: int) -> Optional[Dict]:
        """Получает запрос по ID."""
        history = self._load_history()
        for record in history:
            if record['id'] == request_id:
                return record
        return None
    
    def clear_history(self):
        """Очищает всю историю."""
        self._save_history([])
        logger.info("История запросов очищена")
    
    def delete_request(self, request_id: int) -> bool:
        """Удаляет запрос по ID."""
        history = self._load_history()
        original_length = len(history)
        
        history = [record for record in history if record['id'] != request_id]
        
        if len(history) < original_length:
            # Обновляем ID
            for i, record in enumerate(history):
                record['id'] = i + 1
            
            self._save_history(history)
            logger.info(f"Удален запрос из истории: ID {request_id}")
            return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Получает статистику по истории."""
        history = self._load_history()
        
        if not history:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_characters': 0,
                'average_characters': 0,
                'total_sentences': 0,
                'average_sentences': 0
            }
        
        successful = [r for r in history if r['success']]
        failed = [r for r in history if not r['success']]
        
        total_chars = sum(r.get('char_count', 0) for r in successful)
        total_sentences = sum(r.get('sentence_count', 0) for r in successful)
        
        return {
            'total_requests': len(history),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'total_characters': total_chars,
            'average_characters': total_chars // len(successful) if successful else 0,
            'total_sentences': total_sentences,
            'average_sentences': total_sentences // len(successful) if successful else 0
        }


# Глобальный экземпляр менеджера истории
history_manager = HistoryManager() 