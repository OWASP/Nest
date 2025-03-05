"""Typesense index for User model."""

from apps.common.typesense import IndexBase, register


@register("user")
class UserIndex(IndexBase):
    """Typesense index for User model."""

    index_name = "user"
    schema = {
        "name": "user",
        "enable_nested_fields": True,
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "avatar_url", "type": "string"},
            {"name": "bio", "type": "string"},
            {"name": "company", "type": "string"},
            {"name": "contributions", "type": "string[]"},
            {"name": "created_at", "type": "float"},
            {"name": "email", "type": "string"},
            {"name": "followers_count", "type": "int32"},
            {"name": "following_count", "type": "int32"},
            {"name": "issues_count", "type": "int32"},
            {"name": "key", "type": "string"},
            {"name": "location", "type": "string"},
            {"name": "login", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "public_repositories_count", "type": "int32"},
            {"name": "title", "type": "string"},
            {"name": "updated_at", "type": "float"},
            {"name": "url", "type": "string"},
        ],
        "default_sorting_field": "updated_at",
    }

    def prepare_document(self, user):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(user.id) if user.id else "",
            "avatar_url": user.idx_avatar_url or "",
            "bio": user.idx_bio or "",
            "company": user.idx_company or "",
            "contributions": user.idx_contributions if user.idx_contributions else [],
            "created_at": user.idx_created_at if user.idx_created_at is not None else 0,
            "email": user.idx_email or "",
            "followers_count": user.idx_followers_count
            if user.idx_followers_count is not None
            else 0,
            "following_count": user.idx_following_count
            if user.idx_following_count is not None
            else 0,
            "issues_count": user.idx_issues_count if user.idx_issues_count is not None else 0,
            "key": user.idx_key or "",
            "location": user.idx_location or "",
            "login": user.idx_login or "",
            "name": user.idx_name or "",
            "public_repositories_count": user.idx_public_repositories_count
            if user.idx_public_repositories_count is not None
            else 0,
            "title": user.idx_title or "",
            "updated_at": user.idx_updated_at if user.idx_updated_at is not None else 0,
            "url": user.idx_url or "",
        }
