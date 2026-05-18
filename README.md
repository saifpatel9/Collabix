# Collabix

Collabix is a production-oriented internal workflow management foundation built for a single company using Django, Django REST Framework, HTMX, Alpine.js, Tailwind CSS, MySQL, Redis, Channels, Docker, Gunicorn, and Nginx.

## Architecture Highlights

- Single-company architecture with modular bounded apps instead of multi-tenant complexity.
- Clean separation between domain logic, services, selectors, API, views, and websocket layers.
- Server-side rendered dashboard shell with HTMX enhancement points and Alpine.js for local UI state.
- ASGI-ready runtime prepared for realtime notifications through Redis-backed Django Channels.
- Environment-driven configuration split for development and production.

## Repository Layout

```text
Collabix/
├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── attendance/
│   │   ├── chat/
│   │   ├── core/
│   │   ├── dashboard/
│   │   ├── employees/
│   │   ├── notifications/
│   │   ├── projects/
│   │   └── tasks/
│   ├── config/
│   │   └── settings/
│   ├── frontend/src/
│   ├── media/uploads/
│   ├── requirements/
│   ├── static/
│   └── templates/
├── docker/
│   └── nginx/
├── docs/
│   ├── architecture/
│   └── standards/
├── env/
├── scripts/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── package.json
└── pyproject.toml
```

## Local Setup

### 1. Prerequisites

- Python 3.12+
- Node.js 20+
- MySQL 8+
- Redis 7+

### 2. Environment

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements/development.txt
npm install
```

### 3. Database

Create a MySQL database and user matching `.env`, or use Docker Compose.

### 4. Run locally

Open separate terminals:

```bash
source .venv/bin/activate
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

```bash
npm run dev
```

```bash
redis-server
```

## Docker Setup

```bash
cp .env.example .env
docker compose up --build
```

Once services are up:

```bash
docker compose exec web python manage.py createsuperuser
```

## Useful Commands

```bash
black backend
python backend/manage.py test
npm run format
docker compose down
```

## Environment Variables

Use `.env.example` as the source of truth. Important groups:

- Django runtime and security
- MySQL connection details
- Redis channel layer URL
- CORS and JWT timing

## Deployment Notes

- Run behind Nginx with TLS terminated at the load balancer or reverse proxy.
- Use `config.settings.production` in production.
- Persist MySQL and media volumes.
- Keep Redis available for Channels.
- Rotate `DJANGO_SECRET_KEY` per environment and do not commit live secrets.
