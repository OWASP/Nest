"""Typesense index for Repository model."""

from apps.common.typesense import IndexBase, register


@register("repository")
class RepositoryIndex(IndexBase):
    """Typesense index for Repository model."""

    index_name = "repository"
    schema = {
        "name": "repository",
        "default_sorting_field": "pushed_at",
        "enable_nested_fields": True,
        "fields": [
            {"name": "commits_count", "type": "int32"},
            {"name": "contributors_count", "type": "int32"},
            {"name": "created_at", "type": "float"},
            {"name": "description", "type": "string"},
            {"name": "forks_count", "type": "int32", "facet": True},
            {"name": "has_funding_yml", "type": "bool"},
            {"name": "key", "type": "string"},
            {"name": "languages", "type": "string[]"},
            {"name": "license", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "open_issues_count", "type": "int32"},
            {"name": "project_key", "type": "string"},
            {"name": "pushed_at", "type": "float", "facet": True},
            {"name": "size", "type": "int32"},
            {"name": "stars_count", "type": "int32", "facet": True},
            {"name": "subscribers_count", "type": "int32"},
            {"name": "topics", "type": "string[]"},
            {
                "name": "top_contributors",
                "type": "object[]",
                "fields": [
                    {"name": "avatar_url", "type": "string"},
                    {"name": "contributions_count", "type": "int32"},
                    {"name": "login", "type": "string"},
                    {"name": "name", "type": "string"},
                ],
                "optional": True,
            },
        ],
    }

    def prepare_document(self, repository):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "commits_count": int(repository.idx_commits_count)
            if repository.idx_commits_count is not None
            else 0,
            "contributors_count": int(repository.idx_contributors_count)
            if repository.idx_contributors_count is not None
            else 0,
            "created_at": float(repository.idx_created_at)
            if repository.idx_created_at is not None
            else 0.0,
            "description": repository.idx_description or "",
            "forks_count": int(repository.idx_forks_count)
            if repository.idx_forks_count is not None
            else 0,
            "has_funding_yml": bool(repository.idx_has_funding_yml)
            if repository.idx_has_funding_yml is not None
            else False,
            "key": repository.idx_key or "",
            "languages": sorted(
                [
                    k
                    for k, v in sorted(
                        getattr(repository, "languages", {}).items(),
                        key=lambda pair: pair[1],
                        reverse=True,
                    )
                ]
            ),
            "license": repository.idx_license or "",
            "name": repository.idx_name or "",
            "open_issues_count": int(repository.idx_open_issues_count)
            if repository.idx_open_issues_count is not None
            else 0,
            "project_key": repository.idx_project_key or "",
            "pushed_at": float(repository.idx_pushed_at)
            if repository.idx_pushed_at is not None
            else 0.0,
            "size": int(repository.idx_size) if repository.idx_size is not None else 0,
            "stars_count": int(repository.idx_stars_count)
            if repository.idx_stars_count is not None
            else 0,
            "subscribers_count": int(repository.idx_subscribers_count)
            if repository.idx_subscribers_count is not None
            else 0,
            "topics": repository.idx_topics if isinstance(repository.idx_topics, list) else [],
            "top_contributors": [
                {
                    "avatar_url": contributor["avatar_url"],
                    "contributions_count": contributor["contributions_count"],
                    "login": contributor["login"],
                    "name": contributor["name"],
                }
                for contributor in repository.idx_top_contributors
            ]
            if repository.idx_top_contributors
            else [],
        }
