chapters_schema = {
    "name": "chapters",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "created_at", "type": "int64"},
        {"name": "location", "type": "geopoint"},
        {"name": "meetup_group", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "postal_code", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "suggested_location", "type": "string"},
        {"name": "updated_at", "type": "int64"},
    ],
    "default_sorting_field": "created_at",
}