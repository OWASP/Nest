# OWASP Schema

A Python package providing JSON schemas for OWASP projects.

## Installation

```bash
pip install owasp-schema
```

## Usage

```python
from owasp_schema import get_schema, list_schemas, chapter_schema

# List all available schemas
print(list_schemas())
# Output: ['chapter', 'committee', 'project']

# Get a specific schema
chapter_schema = get_schema("chapter")

# Or use the pre-loaded schemas
print(chapter_schema["title"])
```

## Available Schemas

- `chapter`: Schema for OWASP chapters
- `committee`: Schema for OWASP committees
- `project`: Schema for OWASP projects

## Development

This package is automatically published to PyPI when schema files change in the main branch using OIDC authentication.

## License

MIT License - see LICENSE file for details.
