FROM node:22-alpine AS assets
WORKDIR /app
COPY package.json ./
RUN npm install
COPY tailwind.config.js postcss.config.js .prettierrc ./
COPY backend ./backend
RUN mkdir -p ./backend/static/dist/css ./backend/static/dist/js && npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements /app/requirements
RUN pip install --upgrade pip && pip install -r /app/requirements/production.txt

COPY backend /app/backend
COPY --from=assets /app/backend/static/dist /app/backend/static/dist
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

WORKDIR /app/backend
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3"]
