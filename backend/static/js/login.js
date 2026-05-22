/* =============================================
   COLLABIX — login.js
   Login Page Logic
   Alpine.js components + utilities
   ============================================= */

// ── Loading Screen (reuse landing pattern) ──
window.addEventListener('load', () => {
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) {
      loader.classList.add('fade-out');
      setTimeout(() => loader.remove(), 450);
    }
  }, 1600);
});

// ── Year in footer ──────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});

// ── Scroll reveal (same observer as landing) ─
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
    { threshold: 0.1, rootMargin: '0px 0px -20px 0px' }
  );

  revealEls.forEach(el => observer.observe(el));
});

// ── Page-level Alpine root ────────────────────
// Placed on <html> so darkMode is at the top of the scope chain —
// the theme toggle anywhere in the page can read and write it directly,
// exactly like the landing page's collabixApp() pattern.
function loginPageRoot() {
  return {
    darkMode: true,
    loading: true,
  };
}

// ── Login Form Alpine component ──────────────
function loginForm() {
  return {

    // Form field values
    fields: {
      email: '',
      password: '',
      remember: false,
    },

    // Validation error messages (empty = no error)
    errors: {
      email: '',
      password: '',
    },

    // Track which fields the user has interacted with
    touched: {
      email: false,
      password: false,
    },

    // UI state flags
    submitting: false,
    showPassword: false,
    successMsg: '',
    errorMsg: '',

    // ── Validators ─────────────────────────────

    validateEmail() {
      this.touched.email = true;
      const val = this.fields.email.trim();

      if (!val) {
        this.errors.email = 'Work email is required.';
        return false;
      }

      // RFC-friendly email pattern
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(val)) {
        this.errors.email = 'Please enter a valid email address.';
        return false;
      }

      this.errors.email = '';
      return true;
    },

    validatePassword() {
      this.touched.password = true;
      const val = this.fields.password;

      if (!val) {
        this.errors.password = 'Password is required.';
        return false;
      }

      if (val.length < 6) {
        this.errors.password = 'Password must be at least 6 characters.';
        return false;
      }

      this.errors.password = '';
      return true;
    },

    validateAll() {
      const emailOk    = this.validateEmail();
      const passwordOk = this.validatePassword();
      return emailOk && passwordOk;
    },

    // ── Submit handler ──────────────────────────

    handleSubmit() {
      // Clear top-level banners
      this.successMsg = '';
      this.errorMsg   = '';

      // Run full validation before submitting
      if (!this.validateAll()) return;

      this.submitting = true;

      // Simulate async authentication (replace with real POST / HTMX call)
      setTimeout(() => {
        this.submitting = false;

        // Demo: treat any @company.com address as success
        if (this.fields.email.toLowerCase().endsWith('@company.com')) {
          this.successMsg = 'Login successful! Redirecting to your workspace…';
          this.fields.password = '';
          this.touched = { email: false, password: false };

          // Simulate redirect after short delay
          setTimeout(() => {
            // window.location.href = '/dashboard';  // uncomment in production
          }, 2000);
        } else {
          // Simulate credentials failure
          this.errorMsg = 'Invalid credentials. Please check your email and password.';
        }
      }, 1400);
    },

    // ── Forgot password ─────────────────────────

    handleForgotPassword() {
      const email = this.fields.email.trim();

      if (!email) {
        // Nudge user to enter their email first
        this.errors.email = 'Enter your work email above, then click Forgot password.';
        this.touched.email = true;
        document.getElementById('login-email')?.focus();
        return;
      }

      // Simulate sending reset email
      this.successMsg = `Password reset instructions sent to ${email}. Check your inbox.`;
      this.errorMsg   = '';
    },


  };
}