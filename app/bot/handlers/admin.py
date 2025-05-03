from telegram import Update
from telegram.ext import ContextTypes
from app.shared.database import get_db
from app.shared.models import User

async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота (/stats)"""
    db = next(get_db())
    user_count = db.query(User).count()
    await update.message.reply_text(
        f"📊 Статистика:\n"
        f"Пользователей: {user_count}"
    )