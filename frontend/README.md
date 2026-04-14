# Frontend

The OWASP Nest frontend is a modern web application built with [Next.js](https://nextjs.org/).

## Tech Stack

| Component         | Technology                         |
| ----------------- | ---------------------------------- |
| **Framework**     | Next.js 16.x (React 19)            |
| **Language**      | TypeScript                         |
| **Styling**       | TailwindCSS 4.x                    |
| **UI Library**    | HeroUI                             |
| **Data Fetching** | Apollo Client (for GraphQL)        |
| **Mapping**       | Leaflet / React Leaflet            |
| **Testing**       | Jest (unit/a11y), Playwright (e2e) |

## Directory Structure

The frontend code lives in this directory. Key directories include:

- `src/` - Application source code (pages, components, hooks).
- `public/` - Static assets.
- `__tests__/` - Automated tests.

## Running Locally

The project uses **Docker** for local development. From the project root:

```bash
# Start all services (frontend, backend, db, cache)
docker compose -f docker-compose/local/compose.yaml up
```

To run the frontend development server directly (requires dependencies installed):

```bash
cd frontend
pnpm install
pnpm run dev
```

## Key Scripts

Common `pnpm` scripts defined in `package.json`:

| Task                   | Command                    |
| ---------------------- | -------------------------- |
| Start dev server       | `pnpm run dev`             |
| Build for production   | `pnpm run build`           |
| Lint code              | `pnpm run lint`            |
| Format code            | `pnpm run format`          |
| Generate GraphQL types | `pnpm run graphql-codegen` |
| Run unit tests         | `pnpm run test:unit`       |

See the `Makefile` for Docker-based convenience targets.

## GraphQL Codegen

TypeScript types for GraphQL operations are auto-generated from the backend schema.

- Configuration: `graphql-codegen.ts`
- Output: `src/types/__generated__/`

Run the codegen with:

```bash
# Requires the backend to be running
pnpm run graphql-codegen
```

## Dependencies

Dependencies are managed with [pnpm](https://pnpm.io/). The main configuration is in `package.json`.

```bash
# Update dependencies
cd frontend && pnpm update
```

## Key Features

The OWASP Nest frontend provides an interface for exploring the OWASP ecosystem—chapters,
projects, members, organizations, contribution opportunities, and community snapshots.

Key capabilities include:

- **Project Discovery** – Browse OWASP projects and learn what each project does.
- **Contribution Opportunities** – Find ways to contribute that match your interests and skills.
- **Interactive Chapter Map** – Visualize OWASP chapters and community presence.
- **Community Members** – Explore OWASP community members and their activity across projects.
- **Organizations** – See organizations linked to OWASP projects and chapters and how they connect across the ecosystem.
- **Community Snapshots** – Recent ecosystem-wide highlights and community activity at a glance.

## External Documentation

- [OWASP Nest DeepWiki](https://deepwiki.com/OWASP/Nest/3-frontend-system)

## Environment Variables

The frontend uses the following environment variables (configured in `frontend/.env`):

### `NEXTAUTH_SECRET`

- **Description**: A random secret used by NextAuth.js to sign and encrypt session tokens and cookies.
- **Example Value**: A 32+ character random string (e.g., generated via `openssl rand -base64 32`).
- **Usage**: **Required** for NextAuth.js to function. Without this, authentication will fail.

### `NEXTAUTH_URL`

- **Description**: The canonical URL of the NextAuth.js application.
- **Example Value**: `http://localhost:3000/`
- **Usage**: Used by NextAuth.js to construct callback URLs during the OAuth flow.

### `NEXT_PUBLIC_API_URL`

- **Description**: The base URL for the application's internal API.
- **Example Value**: `https://nest.owasp.org/`
- **Usage**: Used by frontend components to make API calls.

### `NEXT_PUBLIC_CSRF_URL`

- **Description**: The endpoint used to fetch CSRF tokens for secure API requests.
- **Example Value**: `https://nest.owasp.org/csrf/`
- **Usage**: Required for protecting POST/PUT/DELETE requests from CSRF attacks.

### `NEXT_PUBLIC_ENVIRONMENT`

- **Description**: Specifies the current environment in which the application is running.
- **Example Value**: `production`
- **Usage**: Used for toggling features or logging based on environment (`development`, `production`, etc).

### `NEXT_PUBLIC_GRAPHQL_URL`

- **Description**: The endpoint for the GraphQL API.
- **Example Value**: `https://nest.owasp.org/graphql/`
- **Usage**: Used to send GraphQL queries and mutations from the frontend.

### `NEXT_PUBLIC_GTM_AUTH`

- **Description**: Authentication token for Google Tag Manager (GTM).
- **Example Value**: `XYZabc123`
- **Usage**: Optional; used when previewing or testing GTM in different environments.

### `NEXT_PUBLIC_GTM_ID`

- **Description**: The unique ID for the Google Tag Manager container.
- **Example Value**: `GTM-XXXXXXX`
- **Usage**: Required for integrating Google Tag Manager on the frontend.

### `NEXT_PUBLIC_GTM_PREVIEW`

- **Description**: Used for previewing GTM configurations.
- **Usage**: Optional, used during GTM debugging or testing.

### `NEXT_PUBLIC_IDX_URL`

- **Description**: The base URL for IDX (Indexing Service).
- **Example Value**: `https://nest.owasp.org/idx/`
- **Usage**: Used for services interacting with indexing/search features.

### `NEXT_PUBLIC_IS_PROJECT_HEALTH_ENABLED`

- **Description**: Toggles the project health feature in the UI.
- **Example Value**: `true`
- **Usage**: Set to `true` to enable, `false` to disable.

### `NEXT_PUBLIC_POSTHOG_HOST`

- **Description**: The PostHog analytics host URL.
- **Example Value**: `https://us.i.posthog.com`
- **Usage**: Used for product analytics and feature flags.

### `NEXT_PUBLIC_POSTHOG_KEY`

- **Description**: The PostHog project API key for analytics.
- **Usage**: Authenticates frontend with PostHog.

### `NEXT_PUBLIC_RELEASE_VERSION`

- **Description**: The current release version of the application.
- **Example Value**: `1.0.5`
- **Usage**: Displayed in the app UI or logs for tracking deployments.

### `NEXT_PUBLIC_SENTRY_DSN`

- **Description**: The Data Source Name (DSN) for Sentry error tracking.
- **Example Value**: `https://xyz@sentry.io/123456`
- **Usage**: Enables real-time error tracking and reporting in the frontend.

### `NEXT_SERVER_CSRF_URL`

- **Description**: The CSRF endpoint used by the Next.js server for server-side requests.
- **Example Value**: `http://backend:8000/csrf/`
- **Usage**: Used when the server communicates with the backend (e.g., in Docker, use internal hostname).

### `NEXT_SERVER_DISABLE_SSR`

- **Description**: Disables server-side rendering when set to `true`.
- **Example Value**: `false`
- **Usage**: Used for debugging or specific deployment scenarios.

### `NEXT_SERVER_GITHUB_CLIENT_ID`

- **Description**: The Client ID of your GitHub OAuth App.
- **Example Value**: `Ov23liABCDEF1234567`
- **Usage**: **Required** for "Sign in with GitHub" to work locally. Must be a real Client ID from a registered GitHub OAuth App.

### `NEXT_SERVER_GITHUB_CLIENT_SECRET`

- **Description**: The Client Secret of your GitHub OAuth App.
- **Usage**: **Required** for completing the GitHub OAuth flow. Pairs with `NEXT_SERVER_GITHUB_CLIENT_ID`.

### `NEXT_SERVER_GRAPHQL_URL`

- **Description**: The GraphQL endpoint used by the Next.js server for server-side requests.
- **Example Value**: `http://backend:8000/graphql/`
- **Usage**: Used when the server fetches GraphQL data (e.g., in Docker, use internal hostname).
