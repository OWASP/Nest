"""Typesense client configuration and schema definition."""

import typesense

client = typesense.Client(
    {
        "api_key": "nest_typesense_dev",
        "nodes": [{"host": "nest-typesense", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 2,
    }
)

chapters_schema = {
    "name": "chapters",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "postal_code", "type": "string"},
        {"name": "location", "type": "geopoint"},
        {"name": "suggested_location", "type": "string"},
        {"name": "meetup_group", "type": "string"},
        {"name": "created_at", "type": "int64"},
        {"name": "updated_at", "type": "int64"},
    ],
    "default_sorting_field": "created_at",
}
