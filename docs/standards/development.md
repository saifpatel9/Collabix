# Collabix Development Standards

## Python and Django

- Use Black formatting with 88-character lines.
- Keep models thin; move orchestration into services.
- Every persistent model should inherit shared timestamp behavior and default to UUID identifiers unless there is a strong reason not to.
- Use MySQL-compatible ORM features and avoid database-specific SQL unless isolated behind an adapter.
- Prefer explicit imports and typed function signatures for service boundaries.

## API Conventions

- Namespace endpoints under `/api/v1/`.
- Use plural nouns for resources and action suffixes only for non-resource workflows.
- Standardize response envelopes through shared response helpers and exception handlers.
- Protect endpoints with JWT by default and override permissions intentionally.
- Add throttling classes for login and sensitive endpoints.

## Frontend Conventions

- Keep pages server-rendered first.
- Use HTMX for partial refreshes, in-place actions, and form-driven interactions.
- Use Alpine.js only for local UI state and progressive enhancement.
- Build reusable shell elements under `templates/partials/` and `templates/components/`.
- Keep design tokens and utility abstractions in Tailwind config and shared CSS layers.

## Folder Rules

- Do not place cross-app business logic in views.
- Put read-heavy aggregation into selectors.
- Put side effects and transactions into services.
- Keep app internals private unless explicitly exposed through API or template contracts.
