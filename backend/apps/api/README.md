# API Overview

The OWASP Nest API is divided into two primary interfaces: GraphQL and REST.

## GraphQL API

The GraphQL API is the primary interface used by the OWASP Nest frontend application.

- **Framework**: Built using [Strawberry GraphQL](https://strawberry.rocks/).
- **Endpoint**: `/graphql/`
- **Playground**: An interactive GraphiQL interface is automatically available at `/graphql/` when running the backend in development mode (`DJANGO_CONFIGURATION=Local`).

## REST API (v0)

The REST API is used primarily for programmatic access, integrations, and generating client SDKs.

- **Framework**: Built using [Django Ninja](https://django-ninja.dev/).
- **Base Route**: `/api/v0/`
- **Schema**: Auto-generated OpenAPI (Swagger) specification is available at `/api/v0/openapi.json`.

### Client SDKs

The OpenAPI specification is used to generate official SDKs in various languages:
- [OWASP Nest SDKs (Main Repo)](https://github.com/owasp/nest-sdk)
- [Python SDK](https://github.com/owasp/nest-sdk-python)
- [TypeScript SDK](https://github.com/OWASP/nest-sdk-typescript)
