from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def create_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Функция создания команды")

def setup_teams(application):
    application.add_handler(CommandHandler("create_team", create_team))