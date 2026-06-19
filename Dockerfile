# ============================================================
# Stage 1: Frontend assets build
# ============================================================
FROM node:22-alpine AS assets
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci && npm cache clean --force

COPY tailwind.config.js postcss.config.js .prettierrc ./
COPY backend ./backend
RUN mkdir -p ./backend/static/dist/css ./backend/static/dist/js && \
    npm run build

# ============================================================
# Stage 2: Production runtime
# ============================================================
FROM python:3.12-slim AS runtime

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PYTHONPATH=/app/backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    default-mysql-client \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements /app/requirements
RUN pip install --upgrade pip && \
    pip install -r /app/requirements/development.txt

COPY backend /app/backend
COPY --from=assets /app/backend/static/dist /app/backend/static/dist
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
COPY scripts/start-web.sh /app/scripts/start-web.sh
COPY scripts/start-celery.sh /app/scripts/start-celery.sh
COPY scripts/start-celery-beat.sh /app/scripts/start-celery-beat.sh

RUN chmod +x /app/scripts/entrypoint.sh \
    /app/scripts/start-web.sh \
    /app/scripts/start-celery.sh \
    /app/scripts/start-celery-beat.sh

RUN mkdir -p \
    /app/backend/logs \
    /app/backend/staticfiles \
    /app/backend/media \
    /app/backend/backups/database \
    /app/backend/backups/media && \
    addgroup --system --gid 1001 collabix && \
    adduser --system --uid 1001 --gid 1001 collabix && \
    chown -R collabix:collabix \
        /app/backend/logs \
        /app/backend/staticfiles \
        /app/backend/media \
        /app/backend/backups
    
USER collabix

WORKDIR /app/backend

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
