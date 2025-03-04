"""Typesense index for Chapter model."""

from apps.common.typesense import IndexBase, register


@register("chapter")
class ChapterIndex(IndexBase):
    """Typesense index for Chapter model."""

    index_name = "chapter"
    schema = {
        "name": "chapter",
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

    def prepare_document(self, chapter):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(chapter.id),
            "name": chapter.name,
            "country": chapter.country,
            "region": chapter.region,
            "postal_code": chapter.postal_code,
            "location": [chapter.latitude, chapter.longitude]
            if chapter.latitude is not None and chapter.longitude is not None
            else None,
            "suggested_location": chapter.suggested_location,
            "meetup_group": chapter.meetup_group,
            "created_at": int(chapter.created_at.timestamp()) if chapter.created_at else 0,
            "updated_at": int(chapter.updated_at.timestamp()) if chapter.updated_at else 0,
        }
