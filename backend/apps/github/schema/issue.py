"""Typesense schema for GitHub Issue index."""

from apps.common.typesense import IndexBase, register


@register("issue")
class IssueIndex(IndexBase):
    """Typesense index for GitHub issues."""

    index_name = "issue"
    schema = {
        "name": "issue",
        "enable_nested_fields": True,
        "fields": [
            {"name": "author_login", "type": "string"},
            {"name": "author_name", "type": "string"},
            {"name": "comments_count", "type": "int32"},
            {"name": "created_at", "type": "float"},
            {"name": "hint", "type": "string"},
            {"name": "labels", "type": "string[]"},
            {"name": "project_description", "type": "string"},
            {"name": "project_level", "type": "string"},
            {"name": "project_name", "type": "string"},
            {"name": "project_tags", "type": "string[]"},
            {"name": "project_url", "type": "string"},
            {"name": "repository_contributors_count", "type": "int32"},
            {"name": "repository_description", "type": "string"},
            {"name": "repository_forks_count", "type": "int32"},
            {"name": "repository_languages", "type": "string[]"},
            {"name": "repository_name", "type": "string"},
            {"name": "repository_stars_count", "type": "int32"},
            {"name": "repository_topics", "type": "string[]"},
            {"name": "summary", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "updated_at", "type": "float"},
            {"name": "url", "type": "string", "facet": True},
        ],
        "default_sorting_field": "created_at",
    }

    def prepare_document(self, issue):
        """Convert Issue model instance to a dictionary for Typesense."""
        return {
            "author_login": issue.idx_author_login or "",
            "author_name": issue.idx_author_name or "",
            "comments_count": int(issue.idx_comments_count)
            if issue.idx_comments_count is not None
            else 0,
            "created_at": float(issue.idx_created_at) if issue.idx_created_at is not None else 0.0,
            "hint": issue.idx_hint or "",
            "labels": issue.idx_labels if issue.idx_labels else [],
            "project_description": issue.idx_project_description or "",
            "project_level": issue.idx_project_level or "",
            "project_name": issue.idx_project_name or "",
            "project_tags": issue.idx_project_tags if issue.idx_project_tags else [],
            "project_url": issue.idx_project_url or "",
            "repository_contributors_count": int(issue.idx_repository_contributors_count)
            if issue.idx_repository_contributors_count is not None
            else 0,
            "repository_description": issue.idx_repository_description or "",
            "repository_forks_count": int(issue.idx_repository_forks_count)
            if issue.idx_repository_forks_count is not None
            else 0,
            "repository_languages": issue.idx_repository_languages
            if issue.idx_repository_languages
            else [],
            "repository_name": issue.idx_repository_name or "",
            "repository_stars_count": int(issue.idx_repository_stars_count)
            if issue.idx_repository_stars_count is not None
            else 0,
            "repository_topics": issue.idx_repository_topics
            if issue.idx_repository_topics
            else [],
            "summary": issue.idx_summary or "",
            "title": issue.idx_title or "",
            "updated_at": float(issue.idx_updated_at) if issue.idx_updated_at is not None else 0.0,
            "url": issue.idx_url or "",
        }
