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
            {"name": "is_active", "type": "bool"},
            {"name": "key", "type": "string"},
            {"name": "leaders", "type": "string[]"},
            {"name": "_geoloc", "type": "geopoint", "optional": True},
            {"name": "name", "type": "string"},
            {"name": "postal_code", "type": "string"},
            {"name": "region", "type": "string"},
            {"name": "related_urls", "type": "string[]"},
            {"name": "suggested_location", "type": "string"},
            {"name": "summary", "type": "string"},
            {"name": "tags", "type": "string[]"},
            {"name": "top_contributors",
                "type": "object[]",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "avatar_url", "type": "string"},
                    {"name": "contributions_count", "type": "int32"},
                    {"name": "login", "type": "string"},
            ],
            "optional": True,
            },
            {"name": "updated_at", "type": "int64"},
            {"name": "url", "type": "string"},
        ],
        "default_sorting_field": "created_at",
        "enable_nested_fields": True,
    }

    def prepare_document(self, chapter):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(chapter.id),
            "name": chapter.idx_name,
            "country": chapter.idx_country,
            "created_at": int(chapter.idx_created_at),
            "is_active": chapter.idx_is_active,
            "key": chapter.idx_key,
            "leaders": chapter.idx_leaders if hasattr(chapter, "idx_leaders") else [],
            "_geoloc": [chapter.latitude, chapter.longitude]
            if chapter.latitude is not None and chapter.longitude is not None
            else None,
            "postal_code": chapter.idx_postal_code,
            "region": chapter.idx_region,
            "related_urls": chapter.idx_related_urls if hasattr(chapter, "idx_related_urls") else [],
            "suggested_location": chapter.idx_suggested_location,
            "summary": chapter.idx_summary if hasattr(chapter, "idx_summary") else "",
            "tags": chapter.idx_tags if isinstance(chapter.idx_tags, list) else [],
            "top_contributors": [
                {
                    "avatar_url": contributor["avatar_url"],
                    "contributions_count": contributor["contributions_count"],
                    "login":contributor["login"],
                    "name": contributor["name"],
                }
                for contributor in chapter.idx_top_contributors
            ]
            if chapter.idx_top_contributors
            else [],
            "updated_at": int(chapter.idx_updated_at),
            "url": chapter.idx_url if hasattr(chapter, "idx_url") else "",
        }