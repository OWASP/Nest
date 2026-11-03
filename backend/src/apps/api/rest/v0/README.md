
# OWASP API v0

## Important points

When working on this API, **always follow these rules** to avoid breaking clients:

- The authentication class in `__init__.py` **must be named `ApiKey`**.
  - The client’s `api_key` parameter is automatically derived from this name.
  - **Do not rename this class**, only update its implementation if needed.

- Each API endpoint must have a **unique `operationId`** in the OpenAPI specification.
  - Duplicate `operationId`s will break client SDK generation and cause method conflicts.

- Endpoint naming documentation:
  - [Customize methods](https://www.speakeasy.com/docs/customize/methods)
  - [Customize namespaces](https://www.speakeasy.com/docs/customize/structure/namespaces)
