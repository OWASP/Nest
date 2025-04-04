"""Typesense index for Release model."""

from apps.common.typesense import IndexBase, register


@register("release")
class ReleaseIndex(IndexBase):
    """Typesense index for Release model."""

    index_name = "release"
    schema = {
        "name": "release",
        "enable_nested_fields": True,
        "default_sorting_field": "published_at",
        "fields": [
            {
                "name": "author",
                "facet": True,
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
            {"name": "is_pre_release", "type": "bool"},
            {"name": "name", "type": "string"},
            {"name": "project", "type": "string", "facet": True},
            {"name": "published_at", "type": "int64"},
            {"name": "repository", "type": "string", "facet": True},
            {"name": "tag_name", "type": "string"},
        ],
    }

    def prepare_document(self, release):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "author": [
                {
                    "avatar_url": contributor["avatar_url"],
                    "login": contributor["login"],
                    "name": contributor["name"],
                }
                for contributor in release.idx_author
            ]
            if release.idx_author
            else [],
            "created_at": int(release.idx_created_at) if release.idx_created_at is not None else 0,
            "description": release.idx_description or "",
            "is_pre_release": bool(release.idx_is_pre_release)
            if release.idx_is_pre_release is not None
            else False,
            "name": release.idx_name or "",
            "project": release.idx_project or "",
            "published_at": int(release.idx_published_at)
            if release.idx_published_at is not None
            else 0,
            "repository": release.idx_repository or "",
            "tag_name": release.idx_tag_name or "",
        }
