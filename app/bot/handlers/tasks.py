from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция создания задачи")

def setup_tasks(application):
    application.add_handler(CommandHandler("create_task", create_task))