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
            {"name": "idx_author_login", "type": "string"},
            {"name": "idx_author_name", "type": "string"},
            {"name": "idx_comments_count", "type": "int32"},
            {"name": "idx_created_at", "type": "float"},
            {"name": "idx_hint", "type": "string"},
            {"name": "idx_labels", "type": "string[]"},
            {"name": "idx_project_description", "type": "string"},
            {"name": "idx_project_level", "type": "string"},
            {"name": "idx_project_name", "type": "string"},
            {"name": "idx_project_tags", "type": "string[]"},
            {"name": "idx_project_url", "type": "string"},
            {"name": "idx_repository_contributors_count", "type": "int32"},
            {"name": "idx_repository_description", "type": "string"},
            {"name": "idx_repository_forks_count", "type": "int32"},
            {"name": "idx_repository_languages", "type": "string[]"},
            {"name": "idx_repository_name", "type": "string"},
            {"name": "idx_repository_stars_count", "type": "int32"},
            {"name": "idx_repository_topics", "type": "string[]"},
            {"name": "idx_summary", "type": "string"},
            {"name": "idx_title", "type": "string"},
            {"name": "idx_updated_at", "type": "float"},
            {"name": "idx_url", "type": "string"},
        ],
        "default_sorting_field": "idx_created_at",
    }

    def prepare_document(self, issue):
        """Convert Issue model instance to a dictionary for Typesense."""
        return {
            "idx_author_login": issue.idx_author_login or "",
            "idx_author_name": issue.idx_author_name or "",
            "idx_comments_count": int(issue.idx_comments_count)
            if issue.idx_comments_count is not None
            else 0,
            "idx_created_at": float(issue.idx_created_at)
            if issue.idx_created_at is not None
            else 0.0,
            "idx_hint": issue.idx_hint or "",
            "idx_labels": issue.idx_labels if issue.idx_labels else [],
            "idx_project_description": issue.idx_project_description or "",
            "idx_project_level": issue.idx_project_level or "",
            "idx_project_name": issue.idx_project_name or "",
            "idx_project_tags": issue.idx_project_tags if issue.idx_project_tags else [],
            "idx_project_url": issue.idx_project_url or "",
            "idx_repository_contributors_count": int(issue.idx_repository_contributors_count)
            if issue.idx_repository_contributors_count is not None
            else 0,
            "idx_repository_description": issue.idx_repository_description or "",
            "idx_repository_forks_count": int(issue.idx_repository_forks_count)
            if issue.idx_repository_forks_count is not None
            else 0,
            "idx_repository_languages": issue.idx_repository_languages
            if issue.idx_repository_languages
            else [],
            "idx_repository_name": issue.idx_repository_name or "",
            "idx_repository_stars_count": int(issue.idx_repository_stars_count)
            if issue.idx_repository_stars_count is not None
            else 0,
            "idx_repository_topics": issue.idx_repository_topics
            if issue.idx_repository_topics
            else [],
            "idx_summary": issue.idx_summary or "",
            "idx_title": issue.idx_title or "",
            "idx_updated_at": float(issue.idx_updated_at)
            if issue.idx_updated_at is not None
            else 0.0,
            "idx_url": issue.idx_url or "",
        }
