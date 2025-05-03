const tg = window.Telegram.WebApp;
tg.expand();

document.addEventListener('DOMContentLoaded', async () => {
    const tasksList = document.getElementById('tasks-list');
    const response = await fetch('/api/tasks?user_id=' + tg.initDataUnsafe.user.id);
    const tasks = await response.json();

    tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task-card';
        taskElement.innerHTML = `
            <h3>${task.title}</h3>
            <p>${task.description || 'Нет описания'}</p>
            <a href="/task/${task.id}" class="tg-link">Подробнее</a>
        `;
        tasksList.appendChild(taskElement);
    });

    document.getElementById('create-task-btn').addEventListener('click', () => {
        tg.showPopup({
            title: 'Новая задача',
            message: 'Введите название задачи',
            buttons: [{
                id: 'create',
                type: 'ok',
                text: 'Создать'
            }]
        }, (btnId) => {
            if (btnId === 'create') {
                // Логика создания задачи
            }
        });
    });
});