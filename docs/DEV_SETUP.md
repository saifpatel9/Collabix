# Local Development Setup (Windows)

This project combines a Django backend and a static frontend. These notes help running locally and in Docker.

Prerequisites:
- Python 3.11+ (3.12 recommended)
- Node 18+ (for building front-end assets)
- Git
- Optional: MySQL and Redis if you want to run full stack locally

Quick start (recommended, uses SQLite locally):

1. Copy `.env.example` to `.env` and update secrets.

2. Create and activate a virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements/development.txt
```

3. Build frontend assets (optional, assets are included in repo):

```powershell
cd frontend
npm install
npm run build
cd ..
```

4. Apply migrations and collect static:

```powershell
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

Notes:
- For quick local development without MySQL, set `DJANGO_FORCE_SQLITE=True` in `.env` (development settings fallback added).
- To run with Docker Compose: `docker compose up --build` (ensure `.env` has MySQL/Redis credentials if you want those services enabled).
- If you encounter Unicode/encoding issues in templates, run `python scripts/convert_templates_to_utf8.py` to normalize templates to UTF-8.

Security:
- Do NOT commit real secrets to `.env` or `.env.example`.
- Set `DEBUG=False` in production and configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` properly.

Troubleshooting:
- If migrations fail because of MySQL, ensure MySQL is reachable or enable SQLite fallback.
- If static files 404, run `python manage.py collectstatic` and verify `STATIC_ROOT` is served by your webserver.
