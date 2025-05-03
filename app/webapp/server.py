from flask import Flask, request, jsonify, render_template
from app.shared.database import get_db
from app.shared.models import Task, User
from app.shared.config import Config
from app.shared.security import verify_telegram_data
from __future__ import annotations
import os
import sys
from flask import Flask, jsonify

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.shared.config import Config
from app.shared.database import get_db, Base

app = Flask(__name__)

@app.route('/')
def index():
    """Основной endpoint WebApp"""
    init_data = request.args.get('tgWebAppData')
    
    if not verify_telegram_data(init_data, Config.BOT_TOKEN):
        return "Unauthorized", 401
        
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks_api():
    """API для работы с задачами"""
    db = next(get_db())
    
    if request.method == 'POST':
        data = request.json
        task = Task(
            title=data['title'],
            description=data.get('description'),
            creator_id=data['user_id']
        )
        db.add(task)
        db.commit()
        return jsonify({'id': task.id}), 201
    
    tasks = db.query(Task).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description
    } for task in tasks])

@app.route('/task/<int:task_id>')
def task_detail(task_id):
    """Страница конкретной задачи"""
    return render_template('task_detail.html', task_id=task_id)