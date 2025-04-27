import os
import sqlite3
import logging
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Application as Dispatcher
from telegram.ext.filters import *
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не задан TELEGRAM_BOT_TOKEN в .env файле")

bot = Bot(token=TOKEN)

def get_db_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация структуры базы данных"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                chat_id INTEGER NOT NULL,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        
        # Таблица команд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                admin_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id)
            )
        ''')
        
        # Таблица участников команд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Таблица задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
                priority INTEGER DEFAULT 1,
                team_id INTEGER NOT NULL,
                assignee_id INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (assignee_id) REFERENCES users(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        conn.commit()

init_db()

def register_user(user):
    """Регистрация/обновление данных пользователя"""
    with get_db_connection() as conn:
        try:
            conn.execute(
                '''INSERT OR REPLACE INTO users 
                (id, username, chat_id, first_name, last_name) 
                VALUES (?, ?, ?, ?, ?)''',
                (user.id, user.username, user.id, user.first_name, user.last_name)
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка регистрации пользователя: {e}")

def is_user_admin(user_id, team_id=None):
    """Проверяет, является ли пользователь админом команды"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT 1 FROM teams 
            WHERE admin_id = ? 
        '''
        params = [user_id]
        
        if team_id:
            query += ' AND id = ?'
            params.append(team_id)
            
        cursor.execute(query, params)
        return cursor.fetchone() is not None

def start(update: Update, context):
    """Обработчик команды /start"""
    user = update.effective_user
    register_user(user)
    
    help_text = """
👋 Привет! Я бот для управления задачами в командах.

🔹 Основные команды:
/create_team Название - Создать новую команду
/my_teams - Показать мои команды
/add @username - Добавить участника в команду
/task @username Название - Назначить задачу
/tasks - Показать мои задачи

🔹 Для админов:
/remove @username - Удалить участника
/delete_team - Удалить команду
"""
    update.message.reply_text(help_text)

def create_team(update: Update, context):
    """Создание новой команды"""
    user = update.effective_user
    args = context.args
    
    if not args:
        update.message.reply_text("ℹ️ Используйте: /create_team НазваниеКоманды")
        return
    
    team_name = ' '.join(args).strip()
    if len(team_name) > 50:
        update.message.reply_text("❌ Название команды слишком длинное (макс. 50 символов)")
        return
    
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            # Проверяем, что пользователь не админ другой команды
            cursor.execute('SELECT 1 FROM teams WHERE admin_id = ?', (user.id,))
            if cursor.fetchone():
                update.message.reply_text("❌ Вы уже админ другой команды")
                return
            
            # Создаем команду
            cursor.execute(
                'INSERT INTO teams (name, admin_id) VALUES (?, ?)',
                (team_name, user.id)
            )
            team_id = cursor.lastrowid
            
            # Добавляем создателя в команду
            cursor.execute(
                'INSERT INTO team_members (team_id, user_id) VALUES (?, ?)',
                (team_id, user.id)
            )
            
            conn.commit()
            update.message.reply_text(f"✅ Команда '{team_name}' успешно создана!")
            
        except sqlite3.IntegrityError:
            update.message.reply_text("❌ Команда с таким названием уже существует")
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Ошибка при создании команды: {e}")
            update.message.reply_text("❌ Произошла ошибка при создании команды")

def add_member(update: Update, context):
    """Добавление участника в команду"""
    user = update.effective_user
    args = context.args
    
    if not args:
        update.message.reply_text("ℹ️ Используйте: /add @username")
        return
    
    username = args[0].replace('@', '').strip().lower()
    if not username:
        update.message.reply_text("❌ Неверный формат юзернейма")
        return
    
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            # Находим команду, где пользователь админ
            cursor.execute('''
                SELECT t.id FROM teams t
                WHERE t.admin_id = ?
                LIMIT 1
            ''', (user.id,))
            team = cursor.fetchone()
            
            if not team:
                update.message.reply_text("❌ Вы не админ ни одной команды")
                return
            
            team_id = team['id']
            
            # Находим пользователя для добавления
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            target_user = cursor.fetchone()
            
            if not target_user:
                update.message.reply_text("❌ Пользователь не найден. Он должен сначала запустить бота.")
                return
                
            # Добавляем в команду
            try:
                cursor.execute('''
                    INSERT INTO team_members (team_id, user_id)
                    VALUES (?, ?)
                ''', (team_id, target_user['id']))
                conn.commit()
                
                # Отправляем уведомление новому участнику
                bot.send_message(
                    chat_id=target_user['id'],
                    text=f"🎉 Вас добавили в команду!\n"
                         f"Команда: {team_id}\n"
                         f"Админ: @{user.username}"
                )
                
                update.message.reply_text(f"✅ @{username} успешно добавлен в команду!")
                
            except sqlite3.IntegrityError:
                update.message.reply_text(f"❌ @{username} уже в команде")
                
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Ошибка при добавлении участника: {e}")
            update.message.reply_text("❌ Произошла ошибка при добавлении участника")

def assign_task(update: Update, context):
    """Назначение новой задачи"""
    user = update.effective_user
    args = context.args
    
    if len(args) < 2:
        update.message.reply_text("ℹ️ Используйте: /task @username Название задачи")
        return
    
    assignee_username = args[0].replace('@', '').strip().lower()
    task_title = ' '.join(args[1:]).strip()
    
    if len(task_title) > 100:
        update.message.reply_text("❌ Слишком длинное название задачи (макс. 100 символов)")
        return
    
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            # Проверяем, что отправитель состоит хотя бы в одной команде
            cursor.execute('''
                SELECT t.id FROM teams t
                JOIN team_members tm ON t.id = tm.team_id
                WHERE tm.user_id = ?
                LIMIT 1
            ''', (user.id,))
            team = cursor.fetchone()
            
            if not team:
                update.message.reply_text("❌ Вы не состоите ни в одной команде")
                return
                
            team_id = team['id']
            
            # Находим исполнителя
            cursor.execute('''
                SELECT u.id, u.chat_id FROM users u
                JOIN team_members tm ON u.id = tm.user_id
                WHERE u.username = ? AND tm.team_id = ?
                LIMIT 1
            ''', (assignee_username, team_id))
            assignee = cursor.fetchone()
            
            if not assignee:
                update.message.reply_text(f"❌ @{assignee_username} не найден в вашей команде")
                return
                
            # Создаем задачу
            cursor.execute('''
                INSERT INTO tasks (title, team_id, assignee_id, created_by)
                VALUES (?, ?, ?, ?)
            ''', (task_title, team_id, assignee['id'], user.id))
            task_id = cursor.lastrowid
            
            conn.commit()
            
            # Отправляем уведомление исполнителю
            bot.send_message(
                chat_id=assignee['chat_id'],
                text=f"📌 Новая задача #{task_id}\n"
                     f"Название: {task_title}\n"
                     f"От: @{user.username}\n"
                     f"/complete_{task_id} - Завершить задачу"
            )
            
            update.message.reply_text(f"✅ Задача #{task_id} для @{assignee_username} создана!")
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Ошибка при создании задачи: {e}")
            update.message.reply_text("❌ Произошла ошибка при создании задачи")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        json_data = request.get_json()
        if not json_data:
            logger.error("Пустой JSON в вебхуке")
            return jsonify({"error": "Invalid JSON"}), 400
            
        update = Update.de_json(json_data, bot)
        dispatcher = Dispatcher(bot, None, workers=0)
        
        # Регистрируем обработчики команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("create_team", create_team))
        dispatcher.add_handler(CommandHandler("add", add_member))
        dispatcher.add_handler(CommandHandler("task", assign_task))
        
        dispatcher.process_update(update)
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Ошибка в вебхуке: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)