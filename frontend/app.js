document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const addBtn = document.getElementById('add-btn');
    const tasksList = document.getElementById('tasks-list');

    // Загрузка задач при старте
    loadTasks();

    // Обработчик добавления задачи
    addBtn.addEventListener('click', addTask);

    async function loadTasks() {
        try {
            const response = await fetch('http://localhost:5000/api/tasks');
            const tasks = await response.json();
            
            tasksList.innerHTML = '';
            tasks.forEach(task => {
                const taskElement = document.createElement('div');
                taskElement.className = `task ${task.completed ? 'completed' : ''}`;
                taskElement.innerHTML = `
                    <input type="checkbox" ${task.completed ? 'checked' : ''} 
                           onchange="toggleTask(${task.id}, this.checked)">
                    <span class="task-title">${task.title}</span>
                    <button class="delete-btn" onclick="deleteTask(${task.id})">✕</button>
                `;
                tasksList.appendChild(taskElement);
            });
        } catch (error) {
            console.error('Ошибка загрузки задач:', error);
        }
    }

    async function addTask() {
        const title = taskInput.value.trim();
        if (!title) return;

        try {
            const response = await fetch('http://localhost:5000/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title })
            });

            if (response.ok) {
                taskInput.value = '';
                loadTasks();
            }
        } catch (error) {
            console.error('Ошибка добавления задачи:', error);
        }
    }

    // Глобальные функции для обработки событий в HTML
    window.toggleTask = async (taskId, completed) => {
        await fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'PUT'
        });
        loadTasks();
    };

    window.deleteTask = async (taskId) => {
        await fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        loadTasks();
    };
});