# Backend

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

## Environment Variables

The backend uses the following environment variables (configured in `backend/.env`):

### `DJANGO_ALGOLIA_APPLICATION_ID`

- **Description**: The application ID for Algolia.
- **Example Value**: `APPID123`
- **Usage**: Used by Django to initialize Algolia client for indexing/search.

### `DJANGO_ALGOLIA_EXCLUDED_LOCAL_INDEX_NAMES`

- **Description**: Index names to exclude locally (if any).
- **Usage**: Prevents specific indices from being created in local environments.

### `DJANGO_ALGOLIA_WRITE_API_KEY`

- **Description**: The write API key for Algolia.
- **Usage**: Required for Django backend to write data into Algolia indices.

### `DJANGO_ALLOWED_HOSTS`

- **Description**: A comma-separated list of allowed hosts for the application.
- **Example Value**: `localhost,127.0.0.1`
- **Usage**: Restricts HTTP Host header to prevent host header attacks.

### `DJANGO_AWS_ACCESS_KEY_ID`

- **Description**: AWS access key ID.
- **Usage**: Used for authenticating with AWS services (e.g., S3).

### `DJANGO_AWS_SECRET_ACCESS_KEY`

- **Description**: AWS secret access key.
- **Usage**: Used along with access key ID to authenticate AWS API requests.

### `DJANGO_CONFIGURATION`

- **Description**: Specifies the Django configuration to use.
- **Example Value**: `Production`
- **Usage**: Determines which Django settings class to load.

### `DJANGO_DB_HOST`

- **Description**: The hostname of the database server.
- **Example Value**: `db`
- **Usage**: Used to connect Django to the correct PostgreSQL server.

### `DJANGO_DB_NAME`

- **Description**: The name of the database.
- **Example Value**: `nest`
- **Usage**: Specifies the name of the PostgreSQL database used by Django.

### `DJANGO_DB_PASSWORD`

- **Description**: The password for the database user.
- **Usage**: Authenticates the Django DB user.

### `DJANGO_DB_PORT`

- **Description**: The port number for the database server.
- **Example Value**: `5432`
- **Usage**: Specifies the port for connecting to PostgreSQL.

### `DJANGO_DB_USER`

- **Description**: The username for the database.
- **Example Value**: `postgres`
- **Usage**: Authenticates with the database.

### `DJANGO_ELEVENLABS_API_KEY`

- **Description**: The API key for ElevenLabs text-to-speech service.
- **Usage**: Used for audio generation features.

### `DJANGO_OPEN_AI_SECRET_KEY`

- **Description**: The secret key for OpenAI API.
- **Usage**: Used for OpenAI integration.

### `DJANGO_PUBLIC_IP_ADDRESS`

- **Description**: The IP address to use locally.
- **Usage**: Geographic location related functionality.

### `DJANGO_RELEASE_VERSION`

- **Description**: The release version of the application.
- **Example Value**: `1.0.5`
- **Usage**: Identifies the current backend deployment version.

### `DJANGO_REDIS_AUTH_ENABLED`

- **Description**: Whether Redis requires authentication.
- **Example Value**: `True`
- **Usage**: Enables password authentication for Redis when set to `True`.

### `DJANGO_REDIS_HOST`

- **Description**: The hostname of the Redis server.
- **Example Value**: `cache`
- **Usage**: Used to connect Django to Redis for caching and task queues.

### `DJANGO_REDIS_PASSWORD`

- **Description**: The password for Redis authentication.
- **Usage**: Authenticates with Redis when `DJANGO_REDIS_AUTH_ENABLED` is `True`.

### `DJANGO_SECRET_KEY`

- **Description**: The secret key for Django (used for cryptographic signing).
- **Usage**: Required for session management, tokens, etc.

### `DJANGO_SENTRY_DSN`

- **Description**: The DSN for Sentry (used for error tracking).
- **Example Value**: `https://xyz@sentry.io/654321`
- **Usage**: Enables backend error tracking through Sentry.

### `DJANGO_SLACK_BOT_TOKEN`

- **Description**: The token for the Slack bot.
- **Usage**: Authenticates the bot to send messages to Slack channels.

### `DJANGO_SLACK_SIGNING_SECRET`

- **Description**: The signing secret for Slack.
- **Usage**: Used to verify Slack requests to webhooks.

### `GITHUB_TOKEN`

- **Description**: The token for accessing GitHub APIs.
- **Usage**: Used for making authenticated requests to GitHub (e.g., issues, releases).
