# Project Structure & Organization

## Root Level Structure

```
├── backend/           # Django backend application
├── frontend/          # Next.js frontend application
├── docs/              # MkDocs documentation
├── schema/            # JSON schema definitions and validation
├── docker-compose/    # Docker compose configurations for different environments
├── proxy/             # Nginx proxy configurations
├── cron/              # Cron job configurations
├── cspell/            # Spell checking configuration and tools
└── .kiro/             # Kiro AI assistant configuration
```

## Backend Structure (`backend/`)

- **`apps/`**: Django applications organized by domain
  - Each app follows Django's standard structure (models, views, admin, etc.)
  - Common apps likely include: ai, github, owasp, slack
- **`settings/`**: Django configuration files split by environment
- **`data/`**: Data files, backups, and fixtures
- **`static/`**: Static files for Django admin and API documentation
- **`templates/`**: Django templates
- **`tests/`**: Backend test files
- **`docker/`**: Docker configurations for backend
- **`manage.py`**: Django management script
- **`pyproject.toml`**: Poetry configuration with dependencies and tool settings

## Frontend Structure (`frontend/`)

- **`src/`**: Source code for Next.js application
- **`public/`**: Static assets served by Next.js
- **`__tests__/`**: Frontend test files
- **`docker/`**: Docker configurations for frontend
- **Configuration files**: `next.config.ts`, `tailwind.config.js`, `tsconfig.json`, etc.

## Schema Structure (`schema/`)

- **JSON schema files**: `chapter.json`, `committee.json`, `project.json`, `common.json`
- **`utils/`**: Schema validation utilities
- **`tests/`**: Schema validation tests
- **`docker/`**: Docker configurations for schema validation

## Documentation Structure (`docs/`)

- **`assets/`**: Documentation assets (images, etc.)
- **`docker/`**: Docker configurations for docs
- **`schema/`**: Generated schema documentation
- **`scripts/`**: Documentation generation scripts
- **MkDocs configuration**: `mkdocs.yaml` at root level

## Configuration Files

### Environment & Deployment
- **`.env` files**: Environment-specific configuration in backend/ and frontend/
- **`docker-compose/`**: Separate compose files for local, staging, and production
- **`proxy/`**: Nginx configurations for different environments

### Code Quality & CI/CD
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration
- **`.github/`**: GitHub Actions workflows and templates
- **`trivy.yaml`**: Security scanning configuration
- **`.yamllint`**: YAML linting rules

### Development Tools
- **`.vscode/`**: VS Code workspace settings
- **`cspell/`**: Spell checking configuration and custom dictionary

## Naming Conventions

- **Python**: Snake_case for variables, functions, and file names
- **TypeScript/JavaScript**: camelCase for variables and functions, PascalCase for components
- **Django apps**: Lowercase, descriptive names (e.g., `github`, `owasp`, `slack`)
- **Docker services**: Kebab-case with `nest-` prefix (e.g., `nest-backend`, `nest-frontend`)

## Key Architectural Patterns

- **Monorepo**: All components in single repository with shared tooling
- **Microservices via Docker**: Each service runs in its own container
- **Domain-driven design**: Backend apps organized by business domain
- **API-first**: Backend provides both REST and GraphQL APIs
- **Component-based frontend**: React components with TypeScript
- **Infrastructure as Code**: Docker compose for environment management