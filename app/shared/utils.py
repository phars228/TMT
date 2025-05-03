from datetime import datetime
from app.shared.database import get_db

def get_user_by_telegram_id(telegram_id):
    db = next(get_db())
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def format_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'created_at': task.created_at.strftime('%d.%m.%Y %H:%M'),
        'creator': task.creator.first_name
    }