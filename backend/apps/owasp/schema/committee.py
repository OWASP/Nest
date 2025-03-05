"""Typesense index for Committee model."""

from apps.common.typesense import IndexBase, register


@register("committee")
class CommitteeIndex(IndexBase):
    """Typesense index for Committee model."""

    index_name = "committee"
    schema = {
        "name": "committee",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "created_at", "type": "int64"},
            {"name": "key", "type": "string"},
            {"name": "leaders", "type": "string[]"},
            {"name": "name", "type": "string"},
            {"name": "related_urls", "type": "string[]"},
            {"name": "summary", "type": "string"},
            {"name": "tags", "type": "string"},
            {
                "name": "top_contributors",
                "type": "object[]",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "avatar_url", "type": "string"},
                    {"name": "url", "type": "string"},
                    {"name": "contributions_count", "type": "int32"},
                ],
            },
            {"name": "updated_at", "type": "float"},
            {"name": "url", "type": "string"},
        ],
        "default_sorting_field": "created_at",
        "enable_nested_fields": True,
    }

    def prepare_document(self, committee):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(committee.id),
            "created_at": int(committee.idx_created_at),
            "key": committee.idx_key,
            "leaders": committee.idx_leaders if hasattr(committee, "idx_leaders") else [],
            "name": committee.idx_name,
            "related_urls": committee.idx_related_urls
            if hasattr(committee, "idx_related_urls")
            else [],
            "summary": committee.idx_summary if hasattr(committee, "idx_summary") else "",
            "tags": committee.tags if committee.tags else [],
            "top_contributors": [
                {
                    "name": tc["name"],
                    "avatar_url": tc["avatar_url"],
                    "url": f"https://github.com/{tc['login']}",
                    "contributions_count": tc["contributions_count"],
                }
                for tc in committee.idx_top_contributors
            ]
            if committee.idx_top_contributors
            else [],
            "updated_at": int(committee.idx_updated_at),
            "url": committee.idx_url if hasattr(committee, "idx_url") else "",
        }
