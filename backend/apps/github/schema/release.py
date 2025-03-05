"""Typesense index for Release model."""

from apps.common.typesense import IndexBase, register


@register("release")
class ReleaseIndex(IndexBase):
    """Typesense index for Release model."""

    index_name = "release"
    schema = {
        "name": "release",
        "enable_nested_fields": True,
        "fields": [
            {"name": "id", "type": "string"},
            {
                "name": "author",
                "type": "object[]",
                "fields": [
                    {"name": "avatar_url", "type": "string"},
                    {"name": "name", "type": "string"},
                    {"name": "login", "type": "string"},
                ],
                "optional": True,
            },
            {"name": "created_at", "type": "int64"},
            {"name": "description", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "project", "type": "string"},
            {"name": "published_at", "type": "int64"},
            {"name": "repository", "type": "string"},
            {"name": "tag_name", "type": "string"},
            {"name": "is_pre_release", "type": "bool"},
        ],
        "default_sorting_field": "published_at",
    }

    def prepare_document(self, release):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(release.id) if release.id else "",
            "author": [
                {
                    "name": contributor["name"],
                    "avatar_url": contributor["avatar_url"],
                    "login": contributor["login"],
                }
                for contributor in release.idx_author
            ]
            if release.idx_author
            else [],
            "created_at": int(release.idx_created_at) if release.idx_created_at is not None else 0,
            "description": release.idx_description or "",
            "name": release.idx_name or "",
            "project": release.idx_project or "",
            "published_at": int(release.idx_published_at)
            if release.idx_published_at is not None
            else 0,
            "repository": release.idx_repository or "",
            "tag_name": release.idx_tag_name or "",
            "is_pre_release": bool(release.idx_is_pre_release)
            if release.idx_is_pre_release is not None
            else False,
        }
