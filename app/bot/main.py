import logging
from telegram.ext import ApplicationBuilder
from app.shared.database import init_db
from app.shared.config import Config
from app.bot.handlers import setup_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def post_init(app):
    init_db()
    logging.info("База данных готова")

def main():
    application = ApplicationBuilder() \
        .token(Config.BOT_TOKEN) \
        .post_init(post_init) \
        .build()
    
    setup_handlers(application)
    application.run_polling()

if __name__ == "__main__":
    main()