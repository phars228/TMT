const tg = window.Telegram.WebApp;
tg.MainButton.setText('Сохранить').show();

document.addEventListener('DOMContentLoaded', async () => {
    const taskId = new URLSearchParams(window.location.search).get('id');
    const response = await fetch(`/api/tasks/${taskId}`);
    const task = await response.json();

    document.getElementById('task-title').textContent = task.title;
    document.getElementById('task-description').textContent = task.description || 'Нет описания';

    document.getElementById('complete-btn').addEventListener('click', () => {
        tg.sendData(JSON.stringify({
            action: 'complete_task',
            task_id: taskId
        }));
    });
});