// Socket.IO Initialization
const socket = io();

socket.on('task_updated', (data) => {
    showToast(data.message);
    loadTasks();
    loadAnalytics();
});

// Load data on start
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadAnalytics();
});

// Modal Logic
function toggleModal(show) {
    const modal = document.getElementById('task-modal');
    modal.style.display = show ? 'block' : 'none';
}

// API Functions
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        const taskList = document.getElementById('task-list');
        taskList.innerHTML = '';

        tasks.forEach(task => {
            const item = document.createElement('div');
            item.className = `task-item status-${task.status}`;
            item.innerHTML = `
                <div class="task-info">
                    <h4>${task.title}</h4>
                    <p>${task.description || 'No description'}</p>
                </div>
                <div class="task-meta">
                    <span class="badge priority-${task.priority}">${task.priority}</span>
                    <button class="btn-action" onclick="toggleTaskStatus(${task.id}, '${task.status}')">
                        ${task.status === 'Completed' ? 'Undo' : 'Complete'}
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteTask(${task.id})">Delete</button>
                </div>
            `;
            taskList.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const stats = await response.json();
        
        document.getElementById('total-tasks').textContent = stats.total_tasks;
        document.getElementById('completed-tasks').textContent = stats.completed_tasks;
        document.getElementById('pending-tasks').textContent = stats.pending_tasks;
        document.getElementById('completion-pct').textContent = `${stats.completion_percentage}%`;
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-desc').value;
    const priority = document.getElementById('task-priority').value;

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, priority })
        });

        if (response.ok) {
            toggleModal(false);
            document.getElementById('task-form').reset();
            loadTasks();
            loadAnalytics();
        }
    } catch (error) {
        console.error('Error adding task:', error);
    }
});

async function toggleTaskStatus(id, currentStatus) {
    const newStatus = currentStatus === 'Completed' ? 'Pending' : 'Completed';
    try {
        await fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        loadTasks();
        loadAnalytics();
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
        loadTasks();
        loadAnalytics();
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// Toast Notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}
