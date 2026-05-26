document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('appSidebar');
  document.getElementById('openSidebar')?.addEventListener('click', () => sidebar?.classList.add('open'));
  document.getElementById('closeSidebar')?.addEventListener('click', () => sidebar?.classList.remove('open'));

  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-bs-theme', savedTheme);
  if (themeToggle) {
    themeToggle.innerHTML = savedTheme === 'dark' ? '<i class="fa-regular fa-sun"></i>' : '<i class="fa-regular fa-moon"></i>';
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-bs-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-bs-theme', next);
      localStorage.setItem('theme', next);
      themeToggle.innerHTML = next === 'dark' ? '<i class="fa-regular fa-sun"></i>' : '<i class="fa-regular fa-moon"></i>';
    });
  }

  document.querySelectorAll('[data-counter]').forEach((el) => {
    const target = Number(el.dataset.counter || 0);
    let val = 0;
    const step = Math.max(1, Math.ceil(target / 30));
    const timer = setInterval(() => {
      val += step;
      el.textContent = Math.min(val, target);
      if (val >= target) clearInterval(timer);
    }, 30);
  });

  buildCharts();
  setupTableFilterPagination();
  setupSearch();
  setupKanbanDnD();
  setupAuthUX();
});

function buildCharts() {
  if (window.Chart && document.getElementById('taskAnalyticsChart')) {
    new Chart(document.getElementById('taskAnalyticsChart'), {
      type: 'line',
      data: { labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], datasets: [{ label: 'Tasks Completed', data: [48, 56, 51, 63, 72, 67], borderColor: '#4f46e5', backgroundColor: 'rgba(79,70,229,.12)', fill: true, tension: .35 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });
  }
  if (window.Chart && document.getElementById('attendanceChart')) {
    new Chart(document.getElementById('attendanceChart'), {
      type: 'doughnut',
      data: { labels: ['Present', 'Late', 'Absent'], datasets: [{ data: [82, 12, 6], backgroundColor: ['#10b981', '#f59e0b', '#ef4444'] }] },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
  }
  if (window.Chart && document.getElementById('performanceChart')) {
    new Chart(document.getElementById('performanceChart'), {
      type: 'bar',
      data: { labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], datasets: [{ data: [74, 80, 87, 89], backgroundColor: '#6366f1', borderRadius: 8 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } }
    });
  }
}

function setupSearch() {
  const input = document.getElementById('globalSearch');
  if (!input) return;
  input.addEventListener('input', () => {
    const term = input.value.toLowerCase();
    document.querySelectorAll('#employeeTable tbody tr').forEach((row) => {
      row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  });
}

function setupTableFilterPagination() {
  const table = document.getElementById('employeeTable');
  if (!table) return;
  const rows = [...table.querySelectorAll('tbody tr')];
  const roleFilter = document.getElementById('roleFilter');
  const info = document.getElementById('paginationInfo');
  const pagination = document.getElementById('tablePagination');
  const pageSize = 3;
  let page = 1;

  const render = () => {
    const filtered = rows.filter((r) => {
      const role = r.children[1].textContent.trim();
      return !roleFilter.value || role === roleFilter.value;
    });
    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, totalPages);
    rows.forEach((r) => { r.style.display = 'none'; });
    filtered.slice((page - 1) * pageSize, page * pageSize).forEach((r) => { r.style.display = ''; });
    info.textContent = `Showing page ${page} of ${totalPages}`;
    pagination.innerHTML = `<button class="btn btn-sm btn-outline-secondary me-2" ${page === 1 ? 'disabled' : ''} id="pgPrev">Prev</button><button class="btn btn-sm btn-outline-secondary" ${page === totalPages ? 'disabled' : ''} id="pgNext">Next</button>`;
    document.getElementById('pgPrev')?.addEventListener('click', () => { page -= 1; render(); });
    document.getElementById('pgNext')?.addEventListener('click', () => { page += 1; render(); });
  };

  roleFilter?.addEventListener('change', () => { page = 1; render(); });
  render();
}

function setupKanbanDnD() {
  let dragItem = null;
  document.querySelectorAll('.task-card').forEach((card) => {
    card.addEventListener('dragstart', () => { dragItem = card; });
  });
  document.querySelectorAll('[data-dropzone]').forEach((zone) => {
    zone.addEventListener('dragover', (e) => e.preventDefault());
    zone.addEventListener('drop', () => {
      if (dragItem) zone.appendChild(dragItem);
    });
  });
}

function setupAuthUX() {
  document.querySelectorAll('.toggle-password').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.input-group')?.querySelector('.password-field');
      if (!input) return;
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  document.querySelectorAll('.needs-validation').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  const otpInputs = document.querySelectorAll('.otp-row input');
  otpInputs.forEach((input, index) => {
    input.addEventListener('input', () => {
      if (input.value && otpInputs[index + 1]) otpInputs[index + 1].focus();
    });
  });
}
