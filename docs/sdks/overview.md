# API SDKs Overview

OWASP Nest provides a REST API that can be used to generate client SDKs in various programming languages.

## How SDKs are Generated

The REST API is built with [Django Ninja](https://django-ninja.dev/), which automatically generates an OpenAPI (formerly Swagger) specification.

- **OpenAPI Spec URL**: `/api/v0/openapi.json` (when the backend is running).

This specification can be used with SDK generation tools like:

- [Speakeasy](https://www.speakeasy.com/)
- [OpenAPI Generator](https://openapi-generator.tech/)

---

## Important Constraints

When contributing to the REST API, follow these rules to avoid breaking SDK generation:

### 1. Unique `operationId`

Each API endpoint **must have a unique `operationId`** in the OpenAPI spec.

- Duplicate `operationId`s will cause method conflicts in generated SDKs.

### 2. Stable Authentication Class Name

The authentication class in `backend/apps/api/rest/auth/api_key.py` **must be named `ApiKey`**.

- The client's `api_key` parameter is automatically derived from this class name.
- **Do not rename this class.**

---

## Further Reading

- [API v0 README](https://github.com/OWASP/Nest/blob/main/backend/apps/api/rest/v0/README.md) — API development guidelines.
- [Speakeasy: Customize Methods](https://www.speakeasy.com/docs/customize/methods)
- [Speakeasy: Customize Namespaces](https://www.speakeasy.com/docs/customize/structure/namespaces)
