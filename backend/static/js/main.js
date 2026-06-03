/* ==============================================
   COLLABIX — app.js
   Alpine.js Components + HTMX Enhancements
   + Scroll Animations + Counter Logic
   ============================================== */

// ── Loading Screen ──────────────────────────────
window.addEventListener("load", () => {
    setTimeout(() => {
        const loader = document.getElementById("loader");
        if (loader) {
            loader.classList.add("fade-out");
            setTimeout(() => {
                if (loader.parentNode) loader.remove();
            }, 450);
        }
    }, 1200);
});

// ── Year in Footer ──────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    const yearEl = document.getElementById("year");
    if (yearEl) yearEl.textContent = new Date().getFullYear();
});

// ── Main Alpine App ─────────────────────────────
function collabixApp() {
    return {
        loading: true,
        scrolled: false,
        darkMode: localStorage.getItem("landingDarkMode") === "true",

        init() {
            this.applyTheme();
            this.$watch("darkMode", (val) => {
                localStorage.setItem("landingDarkMode", val);
                this.applyTheme();
            });
        },

        applyTheme() {
            if (this.darkMode) {
                document.documentElement.classList.add("dark");
                document.documentElement.classList.remove("light");
            } else {
                document.documentElement.classList.add("light");
                document.documentElement.classList.remove("dark");
            }
        },

        handleScroll() {
            this.scrolled = window.scrollY > 60;
        },

        submitForm(event) {
            const form = event.target;
            const btn = form.querySelector('button[type="submit"]');
            const responseEl = document.getElementById("form-response");
            if (btn) {
                btn.disabled = true;
                const originalText = btn.textContent.trim();
                btn.innerHTML = '<span class="spinner" style="display:inline-block;animation:spin 0.8s linear infinite"></span> Sending…';
            }
            // HTMX will handle the actual POST; this is just visual feedback.
            // If HTMX fails, restore button after timeout.
            setTimeout(() => {
                if (btn && btn.disabled) {
                    btn.disabled = false;
                    btn.innerHTML = 'Send Message';
                }
            }, 8000);
        },
    };
}

// ── Stats Counter Component ─────────────────────
function statsCounter() {
    return {
        counts: {
            employees: 0,
            projects: 0,
            tasks: 0,
            productivity: 0,
        },
        targets: {
            employees: 520,
            projects: 130,
            tasks: 12400,
            productivity: 47,
        },
        started: false,

        startCounting() {
            if (this.started) return;
            this.started = true;
            const duration = 2000;
            const steps = 80;
            const interval = duration / steps;
            const keys = Object.keys(this.targets);
            keys.forEach((key) => {
                const target = this.targets[key];
                let step = 0;
                const inc = target / steps;
                const timer = setInterval(() => {
                    step++;
                    const current = Math.min(Math.round(inc * step), target);
                    this.counts[key] = current;
                    if (step >= steps) clearInterval(timer);
                }, interval);
            });
        },
    };
}

// ── Scroll Reveal (Intersection Observer) ──────
document.addEventListener("DOMContentLoaded", () => {
    const revealEls = document.querySelectorAll(".reveal");
    if (!revealEls.length) return;
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" },
    );
    revealEls.forEach((el) => observer.observe(el));
});

// ── Active Nav Link on Scroll ───────────────────
document.addEventListener("DOMContentLoaded", () => {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-link");
    if (!sections.length || !navLinks.length) return;
    const sectionObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute("id");
                    navLinks.forEach((link) => {
                        link.classList.remove("active");
                        if (link.getAttribute("href") === `#${id}`) {
                            link.classList.add("active");
                        }
                    });
                }
            });
        },
        { threshold: 0.4 },
    );
    sections.forEach((s) => sectionObserver.observe(s));
});

// ── HTMX Contact Response Hook ──────────────────
document.addEventListener("htmx:afterSwap", (evt) => {
    if (evt.target && evt.target.id === "form-response") {
        const btn = document.querySelector('.contact-form button[type="submit"]');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = "Send Message";
        }
        const form = document.querySelector(".contact-form");
        if (form && evt.target.querySelector('[style*="rgba(16,185,129,0.12)"]')) {
            form.reset();
        }
    }
});

// ── HTMX error handler ─────────────────────────
document.addEventListener("htmx:responseError", (evt) => {
    const responseEl = document.getElementById("form-response");
    if (responseEl && evt.detail?.target?.id === "form-response") {
        responseEl.innerHTML = `
            <div style="
              display: flex; align-items: center; gap: 10px;
              background: rgba(239,68,68,0.12);
              border: 1px solid rgba(239,68,68,0.3);
              border-radius: 10px; padding: 14px 18px;
              color: #fca5a5; font-size: 0.9rem; font-weight: 500;
              margin-top: 8px;
            ">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              Something went wrong. Please try again or email us directly.
            </div>
        `;
        const btn = document.querySelector('.contact-form button[type="submit"]');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = "Send Message";
        }
    }
});

// ── Alpine x-intersect polyfill (if plugin missing) ──
document.addEventListener("alpine:init", () => {
    if (typeof Alpine !== "undefined" && !Alpine.directive("intersect")) {
        Alpine.directive("intersect", (el, { expression, modifiers }, { evaluate }) => {
            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            evaluate(expression);
                            if (modifiers.includes("once")) observer.unobserve(el);
                        }
                    });
                },
                { threshold: 0.3 },
            );
            observer.observe(el);
        });
    }
});

// ── Smooth Scroll for all anchor links ──────────
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", (e) => {
            const targetId = anchor.getAttribute("href");
            if (!targetId || targetId === "#") return;
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const navbarHeight = document.querySelector(".navbar")?.offsetHeight || 80;
                const top = target.getBoundingClientRect().top + window.scrollY - navbarHeight - 16;
                window.scrollTo({ top, behavior: "smooth" });
            }
        });
    });
});

// ── Keyboard Accessibility ─────────────────────
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        const menu = document.querySelector(".mobile-menu");
        if (menu && window.getComputedStyle(menu).display !== "none") {
            document.body.click();
        }
    }
});

// ── Navbar active link style injection ──────────
const style = document.createElement("style");
style.textContent = `
  .nav-link.active {
    color: var(--accent) !important;
  }
  .nav-link.active::after {
    left: 14px !important;
    right: 14px !important;
  }
`;
document.head.appendChild(style);

// ── HTMX CSRF Configuration ─────────────────────
document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("htmx:configRequest", (evt) => {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrf) {
            evt.detail.headers["X-CSRFToken"] = csrf.value;
        }
    });
});

/* ── Dashboard / SaaS UI (only runs on dashboard pages) ─────── */
document.addEventListener("DOMContentLoaded", () => {
    if (!document.getElementById("appSidebar")) return;
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
    const sidebar = document.getElementById("appSidebar");
    document.getElementById("openSidebar")?.addEventListener("click", () => sidebar?.classList.add("open"));
    document.getElementById("closeSidebar")?.addEventListener("click", () => sidebar?.classList.remove("open"));
}

function setupTheme() {
    const toggle = document.getElementById("themeToggle");
    const saved = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-bs-theme", saved);
    updateThemeIcon(saved, toggle);
    toggle?.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-bs-theme");
        const next = current === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-bs-theme", next);
        localStorage.setItem("theme", next);
        updateThemeIcon(next, toggle);
    });
}

function updateThemeIcon(theme, target) {
    if (!target) return;
    target.innerHTML = theme === "dark"
        ? '<i class="fa-regular fa-sun"></i>'
        : '<i class="fa-regular fa-moon"></i>';
}

function setupCounters() {
    document.querySelectorAll("[data-counter]").forEach((el) => {
        const target = Number(el.dataset.counter) || 0;
        const hasPercent = el.textContent.includes("%");
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
    const line = document.getElementById("taskAnalyticsChart");
    if (line) {
        new Chart(line, {
            type: "line",
            data: {
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                datasets: [{ data: [42, 53, 48, 67, 71, 78], borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,.16)", fill: true, tension: 0.35 }],
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
        });
    }
    const donut = document.getElementById("attendanceChart");
    if (donut) {
        new Chart(donut, {
            type: "doughnut",
            data: { labels: ["Completed", "In Progress", "At Risk"], datasets: [{ data: [58, 30, 12], backgroundColor: ["#10b981", "#3b82f6", "#ef4444"] }] },
            options: { plugins: { legend: { position: "bottom" } } },
        });
    }
    const bar = document.getElementById("performanceChart");
    if (bar) {
        new Chart(bar, {
            type: "bar",
            data: { labels: ["W1", "W2", "W3", "W4"], datasets: [{ data: [72, 76, 84, 89], backgroundColor: "#14b8a6", borderRadius: 10 }] },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } },
        });
    }
}

function setupTableFeatures() {
    const table = document.getElementById("employeeTable");
    if (!table) return;
    const roleFilter = document.getElementById("roleFilter");
    const search = document.getElementById("tableSearch");
    const info = document.getElementById("paginationInfo");
    const pagination = document.getElementById("tablePagination");
    const headers = table.querySelectorAll("th[data-sort]");
    const pageSize = 3;
    let page = 1;
    let sortBy = "";
    let sortDir = 1;
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    const filteredRows = () => rows.filter((row) => {
        const role = row.children[1]?.textContent.trim();
        const query = (search?.value || "").trim().toLowerCase();
        const roleMatch = !roleFilter?.value || role === roleFilter.value;
        const textMatch = !query || row.textContent.toLowerCase().includes(query);
        return roleMatch && textMatch;
    });
    const render = () => {
        let list = filteredRows();
        if (sortBy) {
            list = list.sort((a, b) => {
                const ai = a.children[sortBy === "name" ? 0 : 1].textContent.trim().toLowerCase();
                const bi = b.children[sortBy === "name" ? 0 : 1].textContent.trim().toLowerCase();
                return ai.localeCompare(bi) * sortDir;
            });
        }
        const total = Math.max(1, Math.ceil(list.length / pageSize));
        if (page > total) page = total;
        rows.forEach((r) => { r.style.display = "none"; });
        list.slice((page - 1) * pageSize, page * pageSize).forEach((r) => { r.style.display = ""; });
        if (info) info.textContent = `Showing page ${page} of ${total}`;
        if (pagination) {
            pagination.innerHTML = `<button id="pgPrev" class="btn btn-sm btn-outline-secondary me-2" ${page === 1 ? "disabled" : ""}>Prev</button><button id="pgNext" class="btn btn-sm btn-outline-secondary" ${page === total ? "disabled" : ""}>Next</button>`;
            document.getElementById("pgPrev")?.addEventListener("click", () => { page -= 1; render(); });
            document.getElementById("pgNext")?.addEventListener("click", () => { page += 1; render(); });
        }
    };
    roleFilter?.addEventListener("change", () => { page = 1; render(); });
    search?.addEventListener("input", () => { page = 1; render(); });
    headers.forEach((header) => header.addEventListener("click", () => {
        const key = header.getAttribute("data-sort");
        if (sortBy === key) sortDir *= -1;
        else { sortBy = key; sortDir = 1; }
        render();
    }));
    render();
}

function setupKanbanDnD() {
    let dragging = null;
    document.querySelectorAll(".task-card").forEach((card) => {
        card.addEventListener("dragstart", () => { dragging = card; });
    });
    document.querySelectorAll("[data-dropzone]").forEach((zone) => {
        zone.addEventListener("dragover", (e) => e.preventDefault());
        zone.addEventListener("drop", () => {
            if (dragging) { zone.appendChild(dragging); showToast("Task moved successfully."); }
        });
    });
}

function setupSearchSuggestions() {
    const input = document.getElementById("globalSearch");
    const list = document.getElementById("searchSuggestions");
    if (!input || !list) return;
    const seed = ["Sprint board", "Design system", "Payroll report", "Bug triage", "Employee attendance"];
    input.addEventListener("input", () => {
        const q = input.value.trim().toLowerCase();
        if (!q) { list.classList.remove("show"); list.innerHTML = ""; return; }
        const results = seed.filter((s) => s.toLowerCase().includes(q)).slice(0, 4);
        list.innerHTML = results.map((r) => `<button type="button">${r}</button>`).join("");
        list.classList.toggle("show", results.length > 0);
    });
    document.addEventListener("click", (e) => {
        if (!list.contains(e.target) && e.target !== input) list.classList.remove("show");
    });
}

function setupNotifications() {
    const container = document.getElementById("notificationList");
    if (!container) return;
    const notifications = ["Standup starts in 20 minutes.", "2 high-priority tasks are overdue.", "Quarterly report generated.", "New team member joined Product squad."];
    container.innerHTML = notifications.map((n) => `<a class="dropdown-item" href="#">${n}</a>`).join("");
}

function setupToastActions() {
    document.querySelectorAll("[data-toast]").forEach((el) => {
        el.addEventListener("click", () => showToast(el.getAttribute("data-toast")));
    });
}

function showToast(message) {
    const body = document.getElementById("toastBody");
    const el = document.getElementById("liveToast");
    if (!body || !el || !window.bootstrap) return;
    body.textContent = message || "Action complete.";
    bootstrap.Toast.getOrCreateInstance(el).show();
}

function setupAuthUX() {
    document.querySelectorAll(".toggle-password").forEach((btn) => {
        btn.addEventListener("click", () => {
            const field = btn.closest(".input-group")?.querySelector(".password-field");
            if (!field) return;
            field.type = field.type === "password" ? "text" : "password";
        });
    });
    document.querySelectorAll(".needs-validation").forEach((form) => {
        form.addEventListener("submit", (e) => {
            if (!form.checkValidity()) { e.preventDefault(); e.stopPropagation(); }
            form.classList.add("was-validated");
        });
    });
}
