"""
Flask веб-приложение для агента page_summarizer.

Предоставляет веб-интерфейс для создания резюме веб-страниц
с историей запросов и логированием через Logtail.
"""

from flask import Flask, render_template, request, jsonify
from agent import summarize_url
from history import history_manager
from logger_config import get_logger

# Настройка логирования
logger = get_logger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница с формой ввода URL."""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """API endpoint для создания резюме."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL не может быть пустым'
            }), 400
        
        logger.info(f"Получен запрос на создание резюме для: {url}")
        
        # Создаем резюме
        summary = summarize_url(url)
        
        # Добавляем в историю
        history_record = history_manager.add_request(url, summary, success=True)
        
        logger.info(f"Резюме успешно создано для: {url} (ID: {history_record['id']})")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'url': url,
            'request_id': history_record['id']
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Ошибка при создании резюме для {url}: {error_msg}")
        
        # Добавляем неудачный запрос в историю
        if 'url' in locals():
            history_record = history_manager.add_request(url, "", success=False, error=error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/history')
def get_history():
    """Получает историю запросов."""
    try:
        limit = request.args.get('limit', type=int)
        history = history_manager.get_history(limit)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history/<int:request_id>')
def get_request(request_id):
    """Получает конкретный запрос по ID."""
    try:
        record = history_manager.get_request_by_id(request_id)
        if record:
            return jsonify({
                'success': True,
                'request': record
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Запрос не найден'
            }), 404
    except Exception as e:
        logger.error(f"Ошибка при получении запроса {request_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    """Удаляет запрос из истории."""
    try:
        success = history_manager.delete_request(request_id)
        if success:
            logger.info(f"Удален запрос из истории: ID {request_id}")
            return jsonify({
                'success': True,
                'message': 'Запрос удален'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Запрос не найден'
            }), 404
    except Exception as e:
        logger.error(f"Ошибка при удалении запроса {request_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history/clear', methods=['DELETE'])
def clear_history():
    """Очищает всю историю."""
    try:
        history_manager.clear_history()
        logger.info("История запросов очищена")
        return jsonify({
            'success': True,
            'message': 'История очищена'
        })
    except Exception as e:
        logger.error(f"Ошибка при очистке истории: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stats')
def get_stats():
    """Получает статистику по истории."""
    try:
        stats = history_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Проверка работоспособности приложения."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 