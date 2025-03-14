"""Typesense index for OWASP common fields."""

TOP_CONTRIBUTOR_FIELD = {
    "name": "top_contributors",
    "type": "object[]",
    "fields": [
        {"name": "avatar_url", "type": "string"},
        {"name": "contributions_count", "type": "int32"},
        {"name": "login", "type": "string"},
        {"name": "name", "type": "string"},
    ],
    "optional": True,
}
