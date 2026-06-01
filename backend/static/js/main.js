/* ==============================================
   COLLABIX — app.js
   Alpine.js Components + HTMX Enhancements
   + Scroll Animations + Counter Logic
   ============================================== */

// ── Loading Screen ──────────────────────────────
window.addEventListener('load', () => {
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) {
      loader.classList.add('fade-out');
      setTimeout(() => loader.remove(), 450);
    }
  }, 1900);
});

// ── Year in Footer ──────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});

// ── Main Alpine App ─────────────────────────────
function collabixApp() {
  return {
    loading: true,
    scrolled: false,

    // Handle scroll state for navbar and scroll-top button
    handleScroll() {
      this.scrolled = window.scrollY > 60;
    },

    // Contact form submission (HTMX intercept fallback)
    submitForm(event) {
      const form = event.target;
      const btn = form.querySelector('button[type="submit"]');
      const responseEl = document.getElementById('form-response');

      // Visual loading state
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Sending…';
      }

      // Simulate async form submission (HTMX handles real POST)
      // This fallback fires when HTMX is not reaching a backend
      setTimeout(() => {
        if (responseEl) {
          responseEl.innerHTML = `
            <div style="
              display: flex; align-items: center; gap: 10px;
              background: rgba(16,185,129,0.12);
              border: 1px solid rgba(16,185,129,0.3);
              border-radius: 10px; padding: 14px 18px;
              color: #6ee7b7; font-size: 0.9rem; font-weight: 500;
              margin-top: 8px;
            ">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Thank you! Your message has been sent. Our team will respond within 1 business day.
            </div>
          `;
        }
        form.reset();
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Send Message';
        }
      }, 1400);
    }
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

      const duration = 2000; // ms
      const steps = 80;
      const interval = duration / steps;

      const keys = Object.keys(this.targets);
      keys.forEach(key => {
        const target = this.targets[key];
        let current = 0;
        let step = 0;
        const inc = target / steps;

        const timer = setInterval(() => {
          step++;
          current = Math.min(Math.round(inc * step), target);
          this.counts[key] = current;
          if (step >= steps) clearInterval(timer);
        }, interval);
      });
    }
  };
}

// ── Scroll Reveal (Intersection Observer) ──────
document.addEventListener('DOMContentLoaded', () => {
  const revealEls = document.querySelectorAll('.reveal');

  if (!revealEls.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    }
  );

  revealEls.forEach(el => observer.observe(el));
});

// ── Active Nav Link on Scroll ───────────────────
document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${id}`) {
              link.classList.add('active');
            }
          });
        }
      });
    },
    { threshold: 0.4 }
  );

  sections.forEach(s => sectionObserver.observe(s));
});

// ── HTMX Contact Form Hook ──────────────────────
document.addEventListener('htmx:afterSwap', (evt) => {
  if (evt.target && evt.target.id === 'form-response') {
    // Ensure HTMX response also shows styled feedback
    const responseEl = document.getElementById('form-response');
    if (responseEl && !responseEl.querySelector('[style]')) {
      responseEl.innerHTML = `
        <div style="
          display: flex; align-items: center; gap: 10px;
          background: rgba(16,185,129,0.12);
          border: 1px solid rgba(16,185,129,0.3);
          border-radius: 10px; padding: 14px 18px;
          color: #6ee7b7; font-size: 0.9rem; font-weight: 500;
          margin-top: 8px;
        ">
          Message sent successfully!
        </div>
      `;
    }
  }
});

// ── Alpine x-intersect polyfill (if plugin missing) ──
// Gracefully handle x-intersect if plugin not loaded
document.addEventListener('alpine:init', () => {
  if (!Alpine.directive('intersect')) {
    Alpine.directive('intersect', (el, { expression, modifiers }, { evaluate }) => {
      const observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              evaluate(expression);
              if (modifiers.includes('once')) observer.unobserve(el);
            }
          });
        },
        { threshold: 0.3 }
      );
      observer.observe(el);
    });
  }
});

// ── Smooth Scroll for all anchor links ──────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 80;
        const top = target.getBoundingClientRect().top + window.scrollY - navbarHeight - 16;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });
});

// ── Keyboard navigation accessibility ──────────
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    // Close mobile menu
    const mobileMenu = document.querySelector('.mobile-menu');
    if (mobileMenu && mobileMenu.style.display !== 'none') {
      // Trigger Alpine close via dispatching click outside
      document.body.click();
    }
  }
});

// ── Navbar active link style injection ──────────
const style = document.createElement('style');
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
