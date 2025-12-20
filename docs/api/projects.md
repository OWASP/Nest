# GET /api/v0/projects/ – List projects

## Overview

Retrieve a paginated list of OWASP projects.

Use this endpoint to obtain project metadata and to discover project keys/IDs that can be used with `GET /api/v0/projects/{project_id}`.

---

## Authentication

In non-local environments (staging and production), this endpoint is protected by an API key:

- The API uses a custom `ApiKey` authentication class that extends `APIKeyHeader`.
- Clients must send a valid API key in the HTTP header:

    X-API-Key: YOUR_API_KEY_VALUE

- If the `X-API-Key` header is missing or invalid, the API returns `401 Unauthorized` with a message indicating a missing or invalid API key.
- Authenticated requests are subject to an auth-based rate limit of **10 requests per second**.

In local development (`IS_LOCAL_ENVIRONMENT`):

- `auth` is disabled and this endpoint is **publicly accessible without authentication**.
- Throttling is disabled.

---

## Request

**Method:** `GET`  
**Path:** `/api/v0/projects/`  

### Query parameters

- `level` (string, query, optional)  
  Level of the project. Must be one of:
  - `other`
  - `incubator`
  - `lab`
  - `production`
  - `flagship`

- `ordering` (string, query, optional)  
  Ordering field. Must be one of:
  - `created_at`
  - `-created_at`
  - `updated_at`
  - `-updated_at`  

  If `ordering` is not provided, the API applies a default ordering in code.

- `page` (integer, query, optional, default: `1`)  
  Page number (must be **>= 1**). If `page` is less than 1 (for example `page=0`), the API returns **422 Unprocessable Content**.

- `page_size` (integer, query, optional, default: `100`)  
  Number of items per page.

### Example request (from OpenAPI “Try it out”, local dev)

```
curl -X 'GET' \
  'http://localhost:8000/api/v0/projects/?level=flagship&ordering=created_at&page=1&page_size=100' \
  -H 'accept: application/json'
```

In a non-local environment, you would also include the API key header:

```
curl -X 'GET' \
  'https://<nest-base-url>/api/v0/projects/?level=flagship&ordering=created_at&page=1&page_size=100' \
  -H 'accept: application/json' \
  -H 'X-API-Key: YOUR_API_KEY_VALUE'
```

---

## Response

### 200 OK – Paginated project list

Media type: `application/json`

#### Example structure (from OpenAPI schema)

> Note: The OpenAPI “Example Value” is illustrative. In live responses, `current_page` is 1-based and reflects the `page` parameter (e.g., `page=1` → `current_page: 1`).

```
{
  "current_page": 0,
  "has_next": true,
  "has_previous": true,
  "items": [
    {
      "created_at": "2025-12-07T23:11:41.450Z",
      "key": "string",
      "level": "other",
      "name": "string",
      "updated_at": "2025-12-07T23:11:41.450Z"
    }
  ],
  "total_count": 0,
  "total_pages": 0
}
```

#### Example when no projects exist (local dev “Try it out”)

```
{
  "current_page": 1,
  "has_next": false,
  "has_previous": false,
  "items": [],
  "total_count": 0,
  "total_pages": 1
}
```

Field overview (based on the schema):

- `current_page`
- `has_next`
- `has_previous`
- `items[]` (array of project objects when present):
  - `created_at`
  - `key`
  - `level`
  - `name`
  - `updated_at`
- `total_count`
- `total_pages`

> Note: In a fresh local development environment (no data synced), `items` may be empty as shown in the “no projects exist” example above.

---
### 404 Not Found — Page out of range

Happens when page is greater than total_pages

```
{
    "detail": "Not Found: Page 2 not found. Valid pages are 1 to 1."
}
```

---

### 422 Unprocessable Content – Invalid query parameters

Returned when query parameters do not match the expected values. For example, sending `level=1` or `ordering=1` results in a response similar to:

```
{
  "detail": [
    {
      "type": "enum",
      "loc": [
        "query",
        "level"
      ],
      "msg": "Input should be 'other', 'incubator', 'lab', 'production' or 'flagship'",
      "ctx": {
        "expected": "'other', 'incubator', 'lab', 'production' or 'flagship'"
      }
    },
    {
      "type": "literal_error",
      "loc": [
        "query",
        "ordering"
      ],
      "msg": "Input should be 'created_at', '-created_at', 'updated_at' or '-updated_at'",
      "ctx": {
        "expected": "'created_at', '-created_at', 'updated_at' or '-updated_at'"
      }
    }
  ]
}
```

To fix, update `level` and `ordering` to one of the valid values listed above.

#### Example – Invalid `page` (e.g., `page=0`)

```
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": [
        "query",
        "page"
      ],
      "msg": "Input should be greater than or equal to 1",
      "ctx": {
        "ge": 1
      }
    }
  ]
}
```

To fix ensure `page` is **>= 1**.
