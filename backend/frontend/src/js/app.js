const STORAGE_KEY = 'taskflow-theme';

function setTheme(mode) {
  document.body.classList.toggle('dark-mode', mode === 'dark');
  localStorage.setItem(STORAGE_KEY, mode);
  const toggles = document.querySelectorAll('[data-theme-toggle]');
  toggles.forEach((btn) => {
    btn.innerHTML = mode === 'dark'
      ? '<i class="fa-regular fa-sun"></i>'
      : '<i class="fa-regular fa-moon"></i>';
  });
}

function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY) || 'light';
  setTheme(saved);
  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const next = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
      setTheme(next);
    });
  });
}

function initCharts() {
  if (!window.Chart) return;
  const velocity = document.getElementById('velocityChart');
  if (velocity) {
    new Chart(velocity, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [{
          label: 'Tasks Completed',
          data: [6, 8, 7, 11, 9, 13],
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6,182,212,.15)',
          fill: true,
          tension: .4
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
  }

  const project = document.getElementById('projectChart');
  if (project) {
    new Chart(project, {
      type: 'doughnut',
      data: {
        labels: ['Done', 'In Progress', 'Todo'],
        datasets: [{ data: [48, 32, 20], backgroundColor: ['#22c55e', '#1d4ed8', '#f59e0b'] }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
  }

  const report = document.getElementById('reportChart');
  if (report) {
    new Chart(report, {
      type: 'bar',
      data: {
        labels: ['Design', 'Frontend', 'Backend', 'QA', 'Ops'],
        datasets: [{ label: 'Hours', data: [42, 55, 48, 36, 29], backgroundColor: '#1d4ed8' }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
  }
}

function initKanban() {
  const cards = document.querySelectorAll('.kanban-card');
  const columns = document.querySelectorAll('.kanban-column');
  cards.forEach((card) => {
    card.addEventListener('dragstart', () => card.classList.add('opacity-50'));
    card.addEventListener('dragend', () => card.classList.remove('opacity-50'));
  });

  columns.forEach((col) => {
    col.addEventListener('dragover', (e) => e.preventDefault());
    col.addEventListener('drop', (e) => {
      e.preventDefault();
      const dragged = document.querySelector('.kanban-card.opacity-50');
      if (dragged) col.appendChild(dragged);
    });
  });
}

function initTaskFilters() {
  const search = document.getElementById('taskSearch');
  if (!search) return;
  search.addEventListener('input', () => {
    const query = search.value.toLowerCase();
    document.querySelectorAll('[data-task-row]').forEach((row) => {
      row.classList.toggle('d-none', !row.textContent.toLowerCase().includes(query));
    });
  });
}

function initNotificationSocket() {
  const widget = document.getElementById('notification-widget');
  if (!widget) return;

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/`);

  socket.addEventListener('message', (event) => {
    const payload = JSON.parse(event.data);
    updateNotificationCount(payload.unread_count);
    if (payload.event === 'notification_summary') return;
    prependNotification(payload);
  });
}

function updateNotificationCount(count) {
  const badge = document.getElementById('notification-count');
  if (!badge) return;
  const value = Number(count || 0);
  badge.textContent = value;
  badge.classList.toggle('hidden', value === 0);
}

function prependNotification(payload) {
  const list = document.getElementById('notification-dropdown-list');
  if (!list) return;
  const empty = list.querySelector('p');
  if (empty) empty.remove();
  const href = payload.action_url || '#';
  const item = document.createElement('a');
  item.href = href;
  item.className = 'block w-full border-b border-slate-100 px-4 py-3 text-left hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800';
  item.innerHTML = `
    <span class="text-sm font-semibold text-cyan-700">${escapeHtml(payload.title)}</span>
    <span class="mt-1 block text-xs text-slate-500">${escapeHtml(payload.message)}</span>
  `;
  list.prepend(item);
}

function escapeHtml(value) {
  return String(value || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initCharts();
  initKanban();
  initTaskFilters();
  initNotificationSocket();
  if (window.AOS) AOS.init({ duration: 700, once: true });
});
