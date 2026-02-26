## OWASP Schema Package

The project uses the `owasp-schema` Python package to parse and validate OWASP project metadata files.

- **Documentation**: [OWASP Schema Docs](https://owasp-schema.readthedocs.io/en/latest/)
- **PyPI**: [owasp-schema](https://pypi.org/project/owasp-schema/)
- **Usage**: See `backend/apps/owasp/management/commands/common/entity_metadata.py`.

This package defines the expected structure for `index.md` and `leaders.md` files within OWASP project repositories.
