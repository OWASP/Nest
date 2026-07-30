# AGENTS

Project-wide conventions for agentic coding tools. Parsed once at conversation
start so agents don't rediscover repo structure every turn.

## Project

OWASP Nest -- a Django/Next.js platform for exploring OWASP projects and
contribution opportunities. MIT license.

## Stack

| Layer       | Technology                                                                 |
| ----------- | -------------------------------------------------------------------------- |
| **Backend** | Python 3.13, Django 6.0, Django Ninja (REST v0), Strawberry GraphQL        |
| **Frontend**| TypeScript, Next.js 16 (React 19), TailwindCSS 4, HeroUI, Apollo Client    |
| **Database**| PostgreSQL 16 + pgvector                                                   |
| **Cache**   | Redis (django-redis, django-rq)                                            |
| **Search**  | Algolia                                                                    |
| **Infra**   | Terraform on AWS                                                           |
| **CI/CD**   | GitHub Actions (29 workflows)                                              |
| **QA**      | pre-commit, ruff, mypy, ESLint, Prettier, CSpell, Semgrep, Trivy, ZAP      |
| **Deps**    | Poetry (backend), pnpm (frontend/cspell/e2e), pip-tools (hashed .txt)      |

## Repository layout

```text
backend/             Django project
  src/apps/           Django applications
    ai/              LLM agent, embeddings, text splitting
    api/             REST v0 endpoints (Django Ninja), GraphQL mutations/queries
    common/          Shared utilities (search, geocoding, OpenAI wrappers)
    core/            Core models (index, tag)
    github/          GitHub API sync (issues, releases, repos, users)
    mentorship/      Mentorship module (programs, modules, mentees)
    nest/            User model, authentication
    owasp/           OWASP models (projects, chapters, committees, events, etc.)
    sitemap/         Sitemap views
    slack/           NestBot Slack bot (commands, events, actions)
  src/settings/      Django configs (base, local, test, production, staging)
  tests/
    unit/apps/       pytest tests mirroring src/apps/ layout
    fuzz/            Schemathesis REST/GraphQL fuzz tests
    cluster-fuzz-lite/  Atheris fuzz harnesses
frontend/            Next.js application
  src/
    app/             App Router pages (projects, chapters, committees, etc.)
    components/      86 React components (cards, forms, charts, map, etc.)
    contexts/        React contexts (BreadcrumbContext)
    hooks/           Custom hooks
    server/          Server utilities (Apollo client, queries)
    types/           TypeScript types + __generated__/ GraphQL types
    utils/           Utility functions (date formatting, URL helpers, etc.)
  __tests__/
    unit/            Jest unit tests
    a11y/            Jest a11y tests (jest-axe)
    mockData/        Test fixtures
infrastructure/      Terraform (bootstrap, live, modules)
  live/              Environment configs (staging, production)
  modules/           Reusable TF modules (networking, service, database, etc.)
docs/                MkDocs material documentation site
  src/               Markdown source files
e2e/                 Playwright e2e tests
tools/               Security/release scripts
cspell/              CSpell spell check config + custom dictionary
docker/              Dockerfiles (backend/{Dockerfile,.local,.unit-tests,.fuzz-tests}, code-checks, frontend, semgrep, ...)
docker-compose/      Compose stacks (local, e2e, fuzz, infrastructure)
make/                Shared Makefile fragments
.github/             GitHub Actions workflows, actions, templates
```

## Django settings

Settings use `django-configurations`. Each class in `backend/src/settings/`
inherits from `Base` and overrides only what differs:

| Class        | File        | Key differences                                         |
| ------------ | ----------- | ------------------------------------------------------- |
| `Base`       | `base.py`   | All apps, middleware, DB, cache, Algolia, Redis config  |
| `Local`      | `local.py`  | Debug on, CSRF/Session Secure off, CORS localhost:3000  |
| `Test`       | `test.py`   | LocMemCache, CSRF/Session Secure off, no SSL redirect   |
| `Staging`    | `staging.py`| S3 storage, Sentry, NestBot disabled, site=nest.owasp.dev|
| `Production` | `production.py`| S3 storage, Sentry, GitHub App auth, site=nest.owasp.org|

The active class is selected by `DJANGO_CONFIGURATION` env var. The
`DJANGO_SETTINGS_MODULE` is always `settings.<name>` (e.g. `settings.test`).

## Common commands

Run everything from the repo root. The project is Docker-first -- most commands
run inside containers.

### Docker images

| Image                | Dockerfile                                       | Use case                        |
| -------------------- | ------------------------------------------------ | ------------------------------- |
| `nest-local-backend` | `docker/backend/Dockerfile.local`                | `make run`, local dev           |
| `nest-test-backend`  | `docker/backend/Dockerfile.unit-tests`           | `make test-backend`             |
| `nest-fuzz-backend`  | `docker/backend/Dockerfile.fuzz-tests`           | `make test-backend-fuzz`        |
| backend production   | `docker/backend/Dockerfile`                      | Docker Compose / ECS deploy     |
| `nest-code-checks`   | `docker/code-checks/Dockerfile`                  | `make check` (lint, format, etc)|

### App lifecycle

| Task                       | Command               |
| -------------------------- | --------------------- |
| Start all services         | `make run`            |
| Create superuser           | `make create-superuser`|
| Run DB migrations          | `make migrate`        |
| Create migrations          | `make migration`      |
| Load fixture data          | `make load-data`      |
| Index data in Algolia      | `make index-data`     |
| Recreate local DB schema   | `make recreate-schema`|
| Sync data from GitHub      | `make sync-data`      |
| Django shell               | `make shell-django`   |
| Backend container shell    | `make exec-backend-command-it CMD=/bin/sh` |

### App management

| Task                       | Command                  |
| -------------------------- | ------------------------ |
| Execute Django command     | `make exec-backend-command CMD="python manage.py <command>"` |
| Interactive backend shell  | `make exec-backend-command-it CMD=/bin/sh`                    |
| Django shell               | `make shell-django`                                           |
| Backend container shell    | `make shell-backend`                                          |
| DB shell                   | `make shell-db`                                               |

### Quality checks

| Task                       | Command               |
| -------------------------- | --------------------- |
| All checks + tests         | `make check-test`     |
| All checks (no tests)      | `make check`          |
| Pre-commit (ruff, mypy, etc)| `make pre-commit`    |
| Prettier (verify)          | `make prettier`       |
| Prettier (auto-fix)        | `make prettier-fix`   |
| ESLint (verify)            | `make eslint`         |
| ESLint (auto-fix)          | `make eslint-fix`     |
| CSpell                     | `make cspell`         |
| Fix prettier + eslint      | `make check-fix`      |
| GraphQL type codegen       | `make graphql-codegen`|

Checks run in the `nest-code-checks` Docker image (auto-built). No host Node,
Python, or Terraform install required.

### Management commands

Data sync and enrichment commands grouped by app. All are Docker-based and run
via `make`:

**GitHub sync** (`backend/make/apps/github.mk`):
- `github-update-owasp-organization` -- fetch OWASP org from GitHub API
- `github-update-users` -- sync GitHub user profiles
- `github-update-related-organizations` -- fetch related orgs
- `github-add-related-repositories` -- add repos from related orgs
- `github-enrich-issues` -- backfill issue metadata from GitHub
- `github-update-pull-requests` -- link PRs to issues via closing keywords

**OWASP data** (`backend/make/apps/owasp.mk`):
- `owasp-scrape-{projects,chapters,committees}` -- scrape OWASP site
- `owasp-enrich-{projects,chapters,committees,events}` -- enrich from GitHub
- `owasp-aggregate-projects` -- consolidate project data
- `owasp-aggregate-entity-contributions` -- aggregate contributors by entity
- `owasp-aggregate-member-contributions` -- tally member activity
- `owasp-update-events` -- fetch events data
- `owasp-update-sponsors` -- fetch sponsors data
- `owasp-sync-posts` -- sync blog posts
- `owasp-update-project-health-{metrics,requirements,scores}` -- compute health
- `owasp-process-snapshots` -- generate community snapshots

**AI/LLM** (`backend/make/apps/ai.mk`):
- `ai-update-{entity}-chunks` -- split entity content into chunks
- `ai-update-{entity}-context` -- generate embeddings and context
- `ai-run-agentic-rag` -- run the agentic RAG pipeline

Entities: chapter, committee, event, project, repository, slack-message.

**Mentorship** (`backend/make/apps/mentorship.mk`):
- `mentorship-sync-issue-levels` -- sync issue difficulty levels
- `mentorship-sync-module-issues` -- sync issues to modules
- `mentorship-update-comments` -- update issue comments

**Slack** (`backend/make/apps/slack.mk`):
- `slack-sync-data` -- sync workspace, members, conversations
- `slack-sync-messages` -- sync channel messages
- `slack-match-owasp-channels` -- link Slack channels to OWASP entities
- `slack-check-invite-link` -- audit invite link usage

**Data pipeline** (`make sync-data` runs the core update stages in order):
1. `github-update-owasp-organization` -- seed org from GitHub
2. `owasp-scrape-{chapters,committees,projects}` -- scrape OWASP site
3. `github-add-related-repositories` -- discover related repos
4. `github-update-related-organizations` -- fetch org metadata
5. `github-update-users` -- sync user profiles
6. `owasp-aggregate-projects` -- consolidate
7. `owasp-aggregate-entity-contributions` -- tally contributors
8. `owasp-aggregate-member-contributions` -- tally member activity
9. `owasp-update-events` -- fetch events
10. `owasp-sync-posts` -- sync blog posts
11. `owasp-update-sponsors` -- fetch sponsor data
12. `slack-sync-data` -- sync Slack state

### Testing

| Task                       | Command                  |
| -------------------------- | ------------------------ |
| All tests                  | `make test`              |
| Backend tests (pytest)     | `make test-backend`      |
| Frontend unit tests (Jest) | `make test-frontend`     |
| E2E tests (Playwright)     | `make test-e2e`          |
| Backend fuzz (Schemathesis)| `make test-backend-fuzz` |
| Security scans (all)       | `make security-scan`     |
| SAST (Semgrep)             | `make security-sast-scan`|
| DAST (ZAP)                 | `make security-dast-scan`|
| Infrastructure tests       | `make test-infrastructure`|

Backend tests use pytest with `--numprocesses=auto` (pytest-xdist), 95%
coverage minimum (`--cov-fail-under=95`). Configuration in `pyproject.toml`
under `[tool.pytest]`. The `conftest.py` at `tests/unit/conftest.py` sets
`NINJA_SKIP_REGISTRY=1` so parallel workers don't trip on NinjaAPI
double-registration -- new test files don't need their own conftest.

Frontend tests use Jest 30 via `@swc/jest`, 95% coverage threshold (branches,
functions, lines, statements). `test:unit` runs `tsc --noEmit` first, then
Jest. Coverage config in `frontend/jest.config.ts`.

### Running outside Docker

The canonical path is Docker. For quick iteration you can run tools directly:

**Backend:**

```bash
cd backend
poetry install
poetry run pytest tests/unit/apps/<app>/ -xvs
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000
```

**Frontend:**

```bash
cd frontend
pnpm install
pnpm run dev
pnpm run test:unit
pnpm run test:a11y
pnpm run lint:check
pnpm run format:check
```

**Pre-commit (host):**

```bash
pip install -r tools/requirements/pre-commit.txt
pre-commit run --all-files
```

Host commands bypass Docker networking (no DB, cache, or backend available
unless those services are running separately). Tests that need PostgreSQL,
Redis, or the full stack must use Docker.

## Dependency management

- **Backend**: Poetry (`backend/pyproject.toml`, `backend/poetry.lock`).
  Hashed pip requirements in `backend/requirements/*.txt` generated via
  `make compile-requirements` (pip-tools from `requirements/*.in`). Update
  with `cd backend && poetry update`.
- **Frontend**: pnpm (`frontend/package.json`, `frontend/pnpm-lock.yaml`).
  Update with `cd frontend && pnpm update`. CI uses `--frozen-lockfile`.
- **Other**: `cspell/`, `e2e/`, `docs/` each have their own `package.json`
  and `pnpm-lock.yaml`. `tools/requirements/pre-commit.txt` is hashed.

Pre-commit, CSpell, and image-scan dependencies install inside Docker
(`nest-code-checks` image). Host installs are only needed for direct
`poetry`/`pnpm` workflows.

## Django models

Base classes in `apps/common/models.py`:

- `TimestampedModel` -- adds `nest_created_at` (auto_now_add) and
  `nest_updated_at` (auto_now) to every model
- `BulkSaveModel` -- provides `bulk_save()` classmethod that batches
  `bulk_create` + `bulk_update` in 1000-row chunks

The `owasp` app models use `RepositoryBasedEntityModel` (from
`apps/owasp/models/common.py`) which extends both and adds a `key` field
used as the URL slug. OWASP models also use `ProjectIndexMixin` and
`ActiveProjectManager` for Algolia indexing and active-project scoping.

GitHub models (`apps/github/models/`) sync data from the GitHub API and include
`Issue`, `PullRequest`, `Release`, `Milestone`, `Repository`, `Organization`,
`User`, `Label`, `Comment`, `Commit`, `RepositoryContributor`.

## API layers

**REST v0** (`/api/v0/`): Django Ninja router in
`apps/api/rest/v0/api.py`. Endpoints per entity:
chapter, committee, event, issue, label, member, milestone, organization,
project, release, repository, snapshot, sponsor. Pagination via
`CustomPagination` (100 per page, cached for 24h).

**GraphQL** (`/graphql/`): Strawberry schema in `settings/graphql.py`.
Queries composed from: `OwaspQuery` (projects, chapters, committees,
events, sponsors, snapshots, board), `GithubQuery` (issues, repos),
`ApiKeyQueries`, `MentorshipQuery`/`ModuleQuery`/`ProgramQuery`.
Mutations composed from: `ApiMutations`, `NestMutations`,
`ModuleMutation`, `ProgramMutation`.

**Internal** (`/idx/`, `/csrf/`, `/status/`): Algolia proxy search,
CSRF token endpoint, health check. Not part of the public API surface.

## NestBot (Slack)

Separate Django app at `apps/slack/`. Architecture:

- **Commands** (22 files in `apps/slack/commands/`): slash command handlers
  (ai, board, chapters, committees, community, contact, contribute, donate,
  events, gsoc, jobs, leaders, news, owasp, policies, projects, sponsor,
  sponsors, staff, users). Base class in `command.py`.
- **Events** (`apps/slack/events/`): app_home_opened, app_mention,
  member_joined_channel, message_posted, team_join, url_verification.
- **Actions** (`apps/slack/actions/`): home tab interactivity.
- **Models**: Conversation, Member, Message, Event, Workspace.
- **Manifest**: `MANIFEST.yaml` -- used for Slack app configuration.
- **Middleware**: CSRF signing verification via Slack SDK.

## Frontend architecture

App Router pages in `frontend/src/app/`:

| Route              | Content                        |
| ------------------ | ------------------------------ |
| `/`                | Home page                      |
| `/projects`        | Project listing + dashboard    |
| `/chapters`        | Chapter listing + map          |
| `/committees`      | Committee listing              |
| `/members`         | Member profiles                |
| `/organizations`   | Organization listing           |
| `/community`       | Community page + snapshots     |
| `/contribute`      | Contribution opportunities     |
| `/about`           | About page                     |
| `/auth/login`      | GitHub OAuth login             |
| `/mentorship`      | Mentorship programs            |
| `/my/mentorship`   | User mentorship portal         |
| `/settings`        | User settings                  |
| `/board`           | Board of directors             |
| `/api/auth`        | NextAuth.js API routes         |
| `/api/health`      | Health check endpoint          |

Data fetching:
- Server components use GraphQL via `server/queries/` (18 query files)
- Client components use Apollo Client (`utils/helpers/apolloClient.ts`)
- REST v0 endpoints used for Algolia-backed searches
- Type definitions in `types/` with GraphQL-generated types in
  `types/__generated__/`

Path aliases (from tsconfig.json):
`app/*`, `components/*`, `hooks/*`, `server/*`, `types/*`, `utils/*`,
`wrappers/*`, `@mockData/*`, `@unit/*`.

## Conventions

- **Python**: ruff (line-length=99), mypy, pre-commit. Run `ruff format` and
  `ruff check --fix` on every `.py` file you touch before committing.
- **TypeScript/JS**: Prettier (printWidth=100, singleQuote, noSemi, trailingComma
  es5), ESLint. Run `make prettier-fix` and `make eslint-fix` before committing.
  Prettier ignores `*.md` (handled by markdownlint via pre-commit), `*.{yaml,yml}`
  (handled by yamlfmt), and `frontend/src/types/__generated__/` (generated
  GraphQL types).
- **Frontend imports**: Use tsconfig path aliases (`components/*`, `utils/*`,
  `hooks/*`, `types/*`, `server/*`, `wrappers/*`) instead of relative paths.
  These are configured in `frontend/tsconfig.json` paths and used across all
  components (e.g. `import Header from 'components/Header'`).
- **No Conventional Commits** in commit messages. Plain imperative mood.
  Example: `Add feature: short description` not `feat: short description`.
- **PRs** target `main`. Must be assigned to an issue first. Unassigned PRs
  auto-closed. Run `make check-test` before pushing.
- **Django**: `django-configurations` for settings classes, `django-ninja` for
  REST, Strawberry for GraphQL. Backend apps in `backend/src/apps/`.
- **Testing**: pytest (pytest-xdist, --numprocesses=auto), 95% coverage minimum.
  Tests mirror source layout under `tests/unit/apps/`. Frontend: Jest via
  @swc/jest, 95% coverage threshold.
- **API**: REST v0 at `/api/v0/` (Django Ninja). GraphQL at `/graphql/`
  (Strawberry). Internal endpoints at `/idx/`, `/csrf/`, `/status/`.
- **Docker Compose**: local stack uses `docker-compose/local/compose.yaml`.
  Volume names on `main` are canonical; feature branches can use overrides.
- **Infrastructure**: Terraform with Terragrunt-style module structure under
  `infrastructure/`. Environments (staging, production) in `infrastructure/live/`.

## Environment files

| File                  | Purpose                              |
| --------------------- | ------------------------------------ |
| `backend/.env`        | Backend local config (from .example) |
| `frontend/.env`       | Frontend local config (from .example)|
| `backend/.env.unit-tests` | Backend unit test overrides      |

Key vars: `DJANGO_SECRET_KEY` (backend, required), `GITHUB_TOKEN` (data sync),
`NEXTAUTH_SECRET` + `NEXT_SERVER_GITHUB_CLIENT_*` (GitHub OAuth).
Full reference in `backend/README.md` and `frontend/README.md`.

## Architecture boundaries

1. Django serves REST v0, GraphQL, CSRF, and Algolia proxy endpoints.
2. NestBot (Slack) is a separate Django app under `apps/slack/` with its own
   commands, events, actions, and views.
3. GitHub sync runs via management commands (`github-update-*`,
   `github-enrich-*`) -- not on the request path.
4. LLM features (AI agent, embeddings, text splitting) live in `apps/ai/`.
5. Frontend fetches data through Apollo Client (GraphQL) or directly (REST v0).
   Server-side queries in `frontend/src/server/queries/`.
6. Deployment is containerized via Docker Compose locally and ECS (Terraform)
   in staging/production.
7. Auth flows through NextAuth.js (GitHub OAuth). The frontend fetches a CSRF
   token from `GET /csrf/` (served by Django) and sends it as `X-CSRFToken` on
   mutating requests. Backend validates via
   `CsrfRefererFallbackMiddleware`. Sessions are signed with `NEXTAUTH_SECRET`
   on the frontend side, `DJANGO_SECRET_KEY` on the backend side.
