import threading
from app.bot.main import main as run_bot
from app.webapp.server import app as web_app
from app.shared.config import Config

def run_webapp():
    """Запуск Flask-приложения"""
    web_app.run(
        host='0.0.0.0',
        port=5001,
        debug=Config.DEBUG
    )

if __name__ == "__main__":
    # Запуск бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запуск веб-приложения в основном потоке
    run_webapp()