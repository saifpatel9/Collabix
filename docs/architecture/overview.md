# Collabix Architecture Overview

## Principles

- Single-company deployment with clear app boundaries.
- Default to server-side rendering, then add HTMX endpoints for partial updates.
- Keep domain rules in `services/` and query composition in `selectors/`.
- Expose external contracts through `api/v1/` and websocket consumers only.
- Centralize shared behavior in `core`.

## Backend Structure

- `apps/<app>/models.py`: persistence models only.
- `apps/<app>/services/`: orchestration and use-case logic.
- `apps/<app>/selectors/`: read/query logic.
- `apps/<app>/api/v1/`: serializers, API views, and URL contracts.
- `apps/<app>/views/`: template-driven views.
- `apps/<app>/websockets/`: consumers and routing.
- `apps/<app>/domain/`: pure business rules and value objects when complexity grows.
- `apps/<app>/infrastructure/`: external adapters, gateways, and integrations.

## Scaling Direction

- Horizontal web scaling through ASGI workers behind Nginx.
- Redis-backed Channels for notification fanout and future chat events.
- UUID-first entities to reduce coupling and support distributed systems.
- Versioned API namespace from the start to preserve future compatibility.
