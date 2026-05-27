document.addEventListener('DOMContentLoaded', () => {
  setupSidebar();
  setupTheme();
  setupCounters();
  setupCharts();
  setupTableFeatures();
  setupKanbanDnD();
  setupSearchSuggestions();
  setupNotifications();
  setupToastActions();
  setupAuthUX();
});

function setupSidebar() {
  const sidebar = document.getElementById('appSidebar');
  document.getElementById('openSidebar')?.addEventListener('click', () => sidebar?.classList.add('open'));
  document.getElementById('closeSidebar')?.addEventListener('click', () => sidebar?.classList.remove('open'));
}

function setupTheme() {
  const toggle = document.getElementById('themeToggle');
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', saved);
  updateThemeIcon(saved, toggle);
  toggle?.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-bs-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next, toggle);
  });
}

function updateThemeIcon(theme, target) {
  if (!target) return;
  target.innerHTML = theme === 'dark' ? '<i class="fa-regular fa-sun"></i>' : '<i class="fa-regular fa-moon"></i>';
}

function setupCounters() {
  document.querySelectorAll('[data-counter]').forEach((el) => {
    const target = Number(el.dataset.counter) || 0;
    const hasPercent = el.textContent.includes('%');
    let current = 0;
    const increment = Math.max(1, Math.ceil(target / 35));
    const t = setInterval(() => {
      current += increment;
      const v = Math.min(current, target);
      el.textContent = hasPercent ? `${v}%` : `${v}`;
      if (v >= target) clearInterval(t);
    }, 26);
  });
}

function setupCharts() {
  if (!window.Chart) return;
  const line = document.getElementById('taskAnalyticsChart');
  if (line) {
    new Chart(line, { type: 'line', data: { labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], datasets: [{ data: [42, 53, 48, 67, 71, 78], borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,.16)', fill: true, tension: .35 }] }, options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
  }

  const donut = document.getElementById('attendanceChart');
  if (donut) {
    new Chart(donut, { type: 'doughnut', data: { labels: ['Completed', 'In Progress', 'At Risk'], datasets: [{ data: [58, 30, 12], backgroundColor: ['#10b981', '#3b82f6', '#ef4444'] }] }, options: { plugins: { legend: { position: 'bottom' } } } });
  }

  const bar = document.getElementById('performanceChart');
  if (bar) {
    new Chart(bar, { type: 'bar', data: { labels: ['W1', 'W2', 'W3', 'W4'], datasets: [{ data: [72, 76, 84, 89], backgroundColor: '#14b8a6', borderRadius: 10 }] }, options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } } });
  }
}

function setupTableFeatures() {
  const table = document.getElementById('employeeTable');
  if (!table) return;

  const roleFilter = document.getElementById('roleFilter');
  const search = document.getElementById('tableSearch');
  const info = document.getElementById('paginationInfo');
  const pagination = document.getElementById('tablePagination');
  const headers = table.querySelectorAll('th[data-sort]');
  const pageSize = 3;
  let page = 1;
  let sortBy = '';
  let sortDir = 1;

  const rows = Array.from(table.querySelectorAll('tbody tr'));

  const filteredRows = () => rows.filter((row) => {
    const role = row.children[1]?.textContent.trim();
    const query = (search?.value || '').trim().toLowerCase();
    const roleMatch = !roleFilter?.value || role === roleFilter.value;
    const textMatch = !query || row.textContent.toLowerCase().includes(query);
    return roleMatch && textMatch;
  });

  const render = () => {
    let list = filteredRows();
    if (sortBy) {
      list = list.sort((a, b) => {
        const ai = a.children[sortBy === 'name' ? 0 : 1].textContent.trim().toLowerCase();
        const bi = b.children[sortBy === 'name' ? 0 : 1].textContent.trim().toLowerCase();
        return ai.localeCompare(bi) * sortDir;
      });
    }

    const total = Math.max(1, Math.ceil(list.length / pageSize));
    if (page > total) page = total;
    rows.forEach((r) => { r.style.display = 'none'; });
    list.slice((page - 1) * pageSize, page * pageSize).forEach((r) => { r.style.display = ''; });

    info.textContent = `Showing page ${page} of ${total}`;
    pagination.innerHTML = `<button id="pgPrev" class="btn btn-sm btn-outline-secondary me-2" ${page === 1 ? 'disabled' : ''}>Prev</button><button id="pgNext" class="btn btn-sm btn-outline-secondary" ${page === total ? 'disabled' : ''}>Next</button>`;
    document.getElementById('pgPrev')?.addEventListener('click', () => { page -= 1; render(); });
    document.getElementById('pgNext')?.addEventListener('click', () => { page += 1; render(); });
  };

  roleFilter?.addEventListener('change', () => { page = 1; render(); });
  search?.addEventListener('input', () => { page = 1; render(); });
  headers.forEach((header) => header.addEventListener('click', () => {
    const key = header.getAttribute('data-sort');
    if (sortBy === key) sortDir *= -1;
    else { sortBy = key; sortDir = 1; }
    render();
  }));

  render();
}

function setupKanbanDnD() {
  let dragging = null;
  document.querySelectorAll('.task-card').forEach((card) => {
    card.addEventListener('dragstart', () => { dragging = card; });
  });

  document.querySelectorAll('[data-dropzone]').forEach((zone) => {
    zone.addEventListener('dragover', (e) => e.preventDefault());
    zone.addEventListener('drop', () => {
      if (dragging) {
        zone.appendChild(dragging);
        showToast('Task moved successfully.');
      }
    });
  });
}

function setupSearchSuggestions() {
  const input = document.getElementById('globalSearch');
  const list = document.getElementById('searchSuggestions');
  if (!input || !list) return;

  const seed = ['Sprint board', 'Design system', 'Payroll report', 'Bug triage', 'Employee attendance'];
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { list.classList.remove('show'); list.innerHTML = ''; return; }
    const results = seed.filter((s) => s.toLowerCase().includes(q)).slice(0, 4);
    list.innerHTML = results.map((r) => `<button type="button">${r}</button>`).join('');
    list.classList.toggle('show', results.length > 0);
  });
  document.addEventListener('click', (e) => {
    if (!list.contains(e.target) && e.target !== input) list.classList.remove('show');
  });
}

function setupNotifications() {
  const container = document.getElementById('notificationList');
  if (!container) return;

  const notifications = [
    'Standup starts in 20 minutes.',
    '2 high-priority tasks are overdue.',
    'Quarterly report generated.',
    'New team member joined Product squad.'
  ];

  container.innerHTML = notifications.map((n) => `<a class="dropdown-item" href="#">${n}</a>`).join('');
}

function setupToastActions() {
  document.querySelectorAll('[data-toast]').forEach((el) => {
    el.addEventListener('click', () => showToast(el.getAttribute('data-toast')));
  });
}

function showToast(message) {
  const body = document.getElementById('toastBody');
  const el = document.getElementById('liveToast');
  if (!body || !el || !window.bootstrap) return;
  body.textContent = message || 'Action complete.';
  bootstrap.Toast.getOrCreateInstance(el).show();
}

function setupAuthUX() {
  document.querySelectorAll('.toggle-password').forEach((btn) => {
    btn.addEventListener('click', () => {
      const field = btn.closest('.input-group')?.querySelector('.password-field');
      if (!field) return;
      field.type = field.type === 'password' ? 'text' : 'password';
    });
  });

  document.querySelectorAll('.needs-validation').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });
}
