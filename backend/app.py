from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Декоратор для проверки авторизации
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token != 'Bearer YOUR_SECRET_TOKEN':
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Получение списка задач
@app.route('/api/tasks', methods=['GET'])
@auth_required
def get_tasks():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    conn = sqlite3.connect('tasks.db')
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.title, t.status, t.created_at, 
                   u.username as assignee, tm.name as team
            FROM tasks t
            JOIN users u ON t.assignee_id = u.id
            JOIN teams tm ON t.team_id = tm.id
            WHERE t.team_id IN (
                SELECT team_id FROM team_members WHERE user_id = ?
            )
            ORDER BY t.created_at DESC
        ''', (user_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "created_at": row[3],
                "assignee": row[4],
                "team": row[5]
            })
        
        return jsonify(tasks)
    finally:
        conn.close()

# Создание задачи
@app.route('/api/tasks', methods=['POST'])
@auth_required
def create_task():
    data = request.json
    required_fields = ['title', 'team_id', 'assignee_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = sqlite3.connect('tasks.db')
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, team_id, assignee_id)
            VALUES (?, ?, ?)
        ''', (data['title'], data['team_id'], data['assignee_id']))
        conn.commit()
        
        return jsonify({"id": cursor.lastrowid}), 201
    finally:
        conn.close()

# Обновление статуса задачи
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@auth_required
def update_task(task_id):
    data = request.json
    if 'status' not in data:
        return jsonify({"error": "status is required"}), 400
    
    conn = sqlite3.connect('tasks.db')
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks SET status = ? WHERE id = ?
        ''', (data['status'], task_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify({"status": "updated"})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(port=5001)