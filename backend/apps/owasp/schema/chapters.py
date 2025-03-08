"""Typesense index for Chapter model."""

from apps.common.typesense import IndexBase, register
from apps.owasp.schema.common import TOP_CONTRIBUTOR_FIELD


@register("chapter")
class ChapterIndex(IndexBase):
    """Typesense index for Chapter model."""

    index_name = "chapter"
    schema = {
        "name": "chapter",
        "default_sorting_field": "created_at",
        "enable_nested_fields": True,
        "fields": [
            {"name": "country", "type": "string", "facet": True},
            {"name": "created_at", "type": "int64"},
            {"name": "is_active", "type": "bool", "facet": True},
            {"name": "key", "type": "string", "facet": True},
            {"name": "leaders", "type": "string[]"},
            {"name": "name", "type": "string", "facet": True},
            {"name": "postal_code", "type": "string"},
            {"name": "region", "type": "string"},
            {"name": "related_urls", "type": "string[]"},
            {"name": "suggested_location", "type": "string"},
            {"name": "summary", "type": "string"},
            {"name": "tags", "type": "string[]", "facet": True},
            {"name": "updated_at", "type": "float"},
            {"name": "url", "type": "string"},
            {"name": "_geoloc", "type": "geopoint", "optional": True},
            TOP_CONTRIBUTOR_FIELD,
        ],
    }

    def prepare_document(self, chapter):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "country": chapter.idx_country,
            "created_at": int(chapter.idx_created_at),
            "is_active": chapter.idx_is_active,
            "key": chapter.idx_key,
            "leaders": chapter.idx_leaders if hasattr(chapter, "idx_leaders") else [],
            "name": chapter.idx_name,
            "postal_code": chapter.idx_postal_code,
            "region": chapter.idx_region,
            "related_urls": chapter.idx_related_urls
            if hasattr(chapter, "idx_related_urls")
            else [],
            "suggested_location": chapter.idx_suggested_location,
            "summary": chapter.idx_summary if hasattr(chapter, "idx_summary") else "",
            "tags": chapter.idx_tags if isinstance(chapter.idx_tags, list) else [],
            "top_contributors": [
                {
                    "avatar_url": contributor["avatar_url"],
                    "contributions_count": contributor["contributions_count"],
                    "login": contributor["login"],
                    "name": contributor["name"],
                }
                for contributor in chapter.idx_top_contributors
            ]
            if chapter.idx_top_contributors
            else [],
            "updated_at": int(chapter.idx_updated_at),
            "url": chapter.idx_url if hasattr(chapter, "idx_url") else "",
            "_geoloc": [chapter.latitude, chapter.longitude]
            if chapter.latitude is not None and chapter.longitude is not None
            else None,
        }
