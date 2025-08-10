# Technology Stack & Build System

## Architecture
- **Backend**: Django 5.1 with Django REST Framework and Strawberry GraphQL
- **Frontend**: Next.js 15 with React 19, TypeScript, and Tailwind CSS
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Cache**: Redis for caching and session management
- **Search**: Algolia for advanced search capabilities
- **AI/ML**: OpenAI integration with LangChain for AI-generated insights

## Key Backend Technologies
- **Framework**: Django with django-configurations
- **API**: Django Ninja (REST) + Strawberry GraphQL
- **Database**: PostgreSQL with pgvector, psycopg2-binary
- **Cache**: django-redis with Redis
- **Search**: algoliasearch-django
- **AI**: OpenAI, LangChain
- **Integrations**: PyGitHub, slack-bolt, slack-sdk
- **Storage**: django-storages with S3 support
- **Monitoring**: Sentry SDK

## Key Frontend Technologies
- **Framework**: Next.js 15 with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS with HeroUI components
- **State Management**: Apollo Client for GraphQL
- **Maps**: Leaflet with marker clustering
- **Charts**: ApexCharts with react-apexcharts
- **Authentication**: NextAuth.js
- **Monitoring**: Sentry

## Package Management
- **Backend**: Poetry (Python 3.13)
- **Frontend**: pnpm (Node.js 22)

## Development Environment
- **Containerization**: Docker with docker-compose
- **Local Development**: docker-compose/local.yaml
- **Services**: Backend (Django), Frontend (Next.js), Database (PostgreSQL), Cache (Redis), Docs (MkDocs)

## Common Commands

### Full Stack Development
```bash
# Start local development environment
make run

# Run all checks (linting, formatting, tests)
make check

# Run tests for entire application
make test

# Clean all dependencies and Docker containers
make clean
```

### Backend Commands
```bash
# Run backend tests
make test-backend

# Django shell access
make django-shell

# Database migrations
make migrate
make migrations

# Load/sync data from external sources
make sync-data
make update-data
make enrich-data
make index-data

# Create superuser
make create-superuser
```

### Frontend Commands
```bash
# Run frontend checks (format + lint)
make check-frontend

# Run frontend tests
make test-frontend

# Update frontend dependencies
make update-frontend-dependencies
```

## Code Quality Tools
- **Backend**: Ruff (linting), pytest (testing), pre-commit hooks
- **Frontend**: ESLint, Prettier, Jest (unit tests), Playwright (e2e tests)
- **Shared**: pre-commit for consistent code quality

## Deployment
- **Production**: docker-compose/production.yaml
- **Staging**: docker-compose/staging.yaml
- **Proxy**: Nginx configuration in proxy/ directory