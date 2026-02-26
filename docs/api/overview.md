--8<-- "backend/apps/api/README.md"

---

## Important Constraints

When contributing to the REST API, follow these rules to avoid breaking SDK generation:

### 1. Unique `operationId`
Each API endpoint **must have a unique `operationId`** in the OpenAPI spec. Duplicate `operationId`s will cause method conflicts in generated SDKs.

### 2. Stable Authentication Class Name
The authentication class in `backend/apps/api/rest/auth/api_key.py` **must be named `ApiKey`**. 
- The client's `api_key` parameter is automatically derived from this class name. 
- **Do not rename this class.**
