from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from app.shared.database import get_db
from app.shared.models.user import User

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    if user:
        await update.message.reply_text(f"Привет, {user.first_name}!")
        return
    
    keyboard = [[InlineKeyboardButton("Войти", callback_data="login")]]
    await update.message.reply_text(
        "Нажмите кнопку для входа:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def login_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    db = next(get_db())
    tg_user = query.from_user
    new_user = User(
        telegram_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )
    
    db.add(new_user)
    db.commit()
    await query.edit_message_text("Вы успешно вошли!")

def setup_auth(application):
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CallbackQueryHandler(login_callback, pattern="^login$"))