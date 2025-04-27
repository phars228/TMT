from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы от фронтенда

# Инициализация БД
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# API для работы с задачами
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, completed FROM tasks')
    tasks = [{'id': row[0], 'title': row[1], 'completed': bool(row[2])} for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Нет названия задачи'}), 400
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title) VALUES (?)', (data['title'],))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': task_id, 'title': data['title'], 'completed': False}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def toggle_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = NOT completed WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)