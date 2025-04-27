document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.expand();
    
    // Элементы интерфейса
    const userInfoEl = document.getElementById('user-info');
    const tasksListEl = document.getElementById('tasks-list');
    const teamMembersEl = document.getElementById('team-members');
    const taskInputEl = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task-btn');
    const memberInputEl = document.getElementById('member-input');
    const addMemberBtn = document.getElementById('add-member-btn');
    
    // Текущий пользователь
    const user = tg.initDataUnsafe.user;
    userInfoEl.textContent = `@${user.username} (${user.first_name})`;
    
    // Переключение вкладок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
            
            if (btn.dataset.tab === 'tasks') {
                loadTasks();
            } else {
                loadTeamMembers();
            }
        });
    });
    
    // Фильтрация задач
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadTasks(btn.dataset.status);
        });
    });
    
    // Добавление задачи
    addTaskBtn.addEventListener('click', addTask);
    taskInputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });
    
    // Добавление участника
    addMemberBtn.addEventListener('click', addTeamMember);
    memberInputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTeamMember();
    });
    
    // Загрузка задач
    async function loadTasks(status = 'all') {
        try {
            const response = await fetch(`/api/tasks?user_id=${user.id}&status=${status}`, {
                headers: {
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                }
            });
            
            if (!response.ok) throw new Error('Ошибка загрузки задач');
            
            const tasks = await response.json();
            renderTasks(tasks);
        } catch (error) {
            console.error('Error:', error);
            tasksListEl.innerHTML = `<div class="error">${error.message}</div>`;
        }
    }
    
    // Отображение задач
    function renderTasks(tasks) {
        if (tasks.length === 0) {
            tasksListEl.innerHTML = '<div class="empty">Нет задач</div>';
            return;
        }
        
        tasksListEl.innerHTML = tasks.map(task => `
            <div class="task ${task.status === 'completed' ? 'completed' : ''}">
                <div class="task-info">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        <span>Команда: ${task.team}</span>
                        <span>Назначено: @${task.assignee}</span>
                        <span>${new Date(task.created_at).toLocaleDateString()}</span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn complete-btn" data-id="${task.id}">
                        ${task.status === 'completed' ? '✓' : 'Завершить'}
                    </button>
                    <button class="task-btn delete-btn" data-id="${task.id}">Удалить</button>
                </div>
            </div>
        `).join('');
        
        // Обработчики для кнопок задач
        document.querySelectorAll('.complete-btn').forEach(btn => {
            btn.addEventListener('click', () => toggleTaskStatus(btn.dataset.id));
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteTask(btn.dataset.id));
        });
    }
    
    // Добавление новой задачи
    async function addTask() {
        const title = taskInputEl.value.trim();
        if (!title) return;
        
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                },
                body: JSON.stringify({
                    title,
                    team_id: 1, // В реальном приложении нужно выбрать команду
                    assignee_id: user.id
                })
            });
            
            if (!response.ok) throw new Error('Ошибка создания задачи');
            
            taskInputEl.value = '';
            loadTasks();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }
    
    // Переключение статуса задачи
    async function toggleTaskStatus(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                },
                body: JSON.stringify({
                    status: 'completed' // В реальном приложении нужно определить текущий статус
                })
            });
            
            if (!response.ok) throw new Error('Ошибка обновления задачи');
            
            loadTasks();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }
    
    // Удаление задачи
    async function deleteTask(taskId) {
        if (!confirm('Удалить задачу?')) return;
        
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                }
            });
            
            if (!response.ok) throw new Error('Ошибка удаления задачи');
            
            loadTasks();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }
    
    // Загрузка участников команды
    async function loadTeamMembers() {
        try {
            const response = await fetch(`/api/teams/1/members`, { // В реальном приложении нужно определить team_id
                headers: {
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                }
            });
            
            if (!response.ok) throw new Error('Ошибка загрузки участников');
            
            const members = await response.json();
            renderTeamMembers(members);
        } catch (error) {
            console.error('Error:', error);
            teamMembersEl.innerHTML = `<div class="error">${error.message}</div>`;
        }
    }
    
    // Отображение участников команды
    function renderTeamMembers(members) {
        if (members.length === 0) {
            teamMembersEl.innerHTML = '<div class="empty">Нет участников</div>';
            return;
        }
        
        teamMembersEl.innerHTML = members.map(member => `
            <div class="team-member">
                <div>@${member.username}</div>
                <button class="task-btn delete-btn" data-id="${member.id}">Удалить</button>
            </div>
        `).join('');
        
        // Обработчики для кнопок удаления
        document.querySelectorAll('.team-member .delete-btn').forEach(btn => {
            btn.addEventListener('click', () => removeTeamMember(btn.dataset.id));
        });
    }
    
    // Добавление участника в команду
    async function addTeamMember() {
        const username = memberInputEl.value.trim().replace('@', '');
        if (!username) return;
        
        try {
            const response = await fetch('/api/teams/1/members', { // В реальном приложении нужно определить team_id
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                },
                body: JSON.stringify({ username })
            });
            
            if (!response.ok) throw new Error('Ошибка добавления участника');
            
            memberInputEl.value = '';
            loadTeamMembers();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }
    
    // Удаление участника из команды
    async function removeTeamMember(userId) {
        if (!confirm('Удалить участника из команды?')) return;
        
        try {
            const response = await fetch(`/api/teams/1/members/${userId}`, { // В реальном приложении нужно определить team_id
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
                }
            });
            
            if (!response.ok) throw new Error('Ошибка удаления участника');
            
            loadTeamMembers();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    }
    
    // Первоначальная загрузка данных
    loadTasks();
});