# Schema Overview

OWASP Nest uses several types of schemas to define its data structures and API contracts.

## Database Schema

The database is PostgreSQL, and the schema is managed through Django's ORM and migrations.

- **Models**: Defined in each Django app under `backend/apps/<app_name>/models/`.
- **Migrations**: Located in `backend/apps/<app_name>/migrations/`.

### Key Commands

| Task              | Command                |
| ----------------- | -----------------------|
| Create migrations | `make migrations`      |
| Apply migrations  | `make migrate`         |
| Recreate schema   | `make recreate-schema` |

---

## API Schemas

### GraphQL Schema

The GraphQL API uses [Strawberry GraphQL](https://strawberry.rocks/). The schema is defined via Python type annotations.

- **Nodes (Types)**: `backend/apps/<app_name>/api/internal/nodes/`
- **Queries**: `backend/apps/<app_name>/api/internal/queries/`

The schema is introspected live from the running backend at `/graphql/`.

### REST API (OpenAPI)

The REST API uses [Django Ninja](https://django-ninja.dev/), which auto-generates an OpenAPI specification.

- **Endpoints**: `backend/apps/api/rest/v0/`
- **OpenAPI Spec**: Available at `/api/v0/openapi.json` when the server is running.

---

## OWASP Schema Package

The project uses the `owasp-schema` Python package to parse and validate OWASP project metadata files.

- **PyPI**: [owasp-schema](https://pypi.org/project/owasp-schema/)
- **Usage**: See `backend/apps/owasp/management/commands/common/entity_metadata.py`.

This package defines the expected structure for `index.md` and `leaders.md` files within OWASP project repositories.
