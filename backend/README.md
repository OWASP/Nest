# Backend Overview

The OWASP Nest backend is a Python-based API server built with the [Django](https://www.djangoproject.com/) framework.

## Tech Stack

| Component       | Technology                                      |
| --------------- | ------------------------------------------------|
| **Framework**   | Django 6.x                                      |
| **REST API**    | [Django Ninja](https://django-ninja.dev/)       |
| **GraphQL API** | [Strawberry GraphQL](https://strawberry.rocks/) |
| **Database**    | PostgreSQL                                      |
| **Caching**     | Redis (via `django-redis`)                      |
| **Task Queue**  | Django RQ                                       |
| **Search**      | Algolia                                         |

## Directory Structure

The backend code lives in this directory. Key directories include:

- `apps/` - Contains all Django applications (e.g., `owasp`, `github`, `api`).
- `settings/` - Django configuration files.
- `tests/` - Automated tests.
- `data/` - Database dumps and backup files.

## Running Locally

The project uses **Docker** for local development. From the project root:

```bash
# Start all services (backend, db, cache)
docker compose -f docker-compose/local/compose.yaml up
```

For common tasks, use the provided `Makefile` targets:

| Task                    | Command                 |
| ----------------------- | ----------------------- |
| Run database migrations | `make migrate`          |
| Create a superuser      | `make create-superuser` |
| Run backend tests       | `make test-backend`     |
| Access Django shell     | `make django-shell`     |

See the root `Makefile` and the local `Makefile` for more targets.

## Key APIs

- **REST API (v0)**: Served at `/api/v0/`. See [API v0 README](https://github.com/OWASP/Nest/blob/main/backend/apps/api/rest/v0/README.md) for SDK-related constraints.
- **GraphQL API**: Served at `/graphql/`.

## Dependencies

Dependencies are managed with [Poetry](https://python-poetry.org/). The main configuration is in `pyproject.toml`.

```bash
# Update dependencies
cd backend && poetry update
```
