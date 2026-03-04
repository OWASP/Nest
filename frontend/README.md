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

## Environment Variables

Configure frontend environment values in `frontend/.env` (copy from `frontend/.env.example`).

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

### `NEXT_PUBLIC_RELEASE_VERSION`

- **Description**: The current release version of the application.
- **Example Value**: `1.0.5`
- **Usage**: Displayed in the app UI or logs for tracking deployments.

### `NEXT_PUBLIC_SENTRY_DSN`

- **Description**: The Data Source Name (DSN) for Sentry error tracking.
- **Example Value**: `https://xyz@sentry.io/123456`
- **Usage**: Enables real-time error tracking and reporting in the frontend.

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
| Run e2e tests          | `pnpm run test:e2e`        |

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

Dependencies are managed with [pnpm](https://pnpm.io/). The configuration is in `package.json`.

```bash
# Update dependencies
cd frontend && pnpm update
```
