"""Typesense index for Project model."""

from apps.common.typesense import IndexBase, register


@register("project")
class ProjectIndex(IndexBase):
    """Typesense index for Project model."""

    index_name = "project"
    schema = {
        "name": "project",
        "enable_nested_fields": True,
        "fields": [
            {"name": "companies", "type": "string[]"},
            {"name": "contributors_count", "type": "int32"},
            {"name": "custom_tags", "type": "string[]"},
            {"name": "description", "type": "string"},
            {"name": "forks_count", "type": "int32"},
            {"name": "id", "type": "string"},
            {"name": "issues_count", "type": "int32"},
            {"name": "is_active", "type": "bool", "facet": True},
            {"name": "key", "type": "string", "facet": True},
            {"name": "languages", "type": "string[]"},
            {"name": "leaders", "type": "string[]"},
            {"name": "level", "type": "string"},
            {"name": "level_raw", "type": "float"},
            {"name": "name", "type": "string", "facet": True},
            {"name": "organizations", "type": "string[]"},
            {
                "name": "repositories",
                "type": "object[]",
                "fields": [
                    {"name": "contributors_count", "type": "int32"},
                    {"name": "description", "type": "string"},
                    {"name": "forks_count", "type": "int32"},
                    {"name": "key", "type": "string"},
                    {"name": "latest_release", "type": "string"},
                    {"name": "license", "type": "string"},
                    {"name": "name", "type": "string"},
                    {"name": "owner_key", "type": "string"},
                    {"name": "stars_count", "type": "int32"},
                ],
            },
            {"name": "repositories_count", "type": "int32"},
            {"name": "stars_count", "type": "int32"},
            {"name": "summary", "type": "string"},
            {"name": "tags", "type": "string[]", "facet": True},
            {"name": "topics", "type": "string[]"},
            {"name": "type", "type": "string"},
            {
                "name": "top_contributors",
                "type": "object[]",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "avatar_url", "type": "string"},
                    {"name": "contributions_count", "type": "int32"},
                    {"name": "login", "type": "string"},
                ],
                "optional": True,
            },
            {"name": "updated_at", "type": "float"},
            {"name": "url", "type": "string"},
        ],
        "default_sorting_field": "updated_at",
    }

    def prepare_document(self, project):
        """Convert model instance to a dictionary for Typesense."""
        return {
            "id": str(project.id) if project.id else "",
            "companies": project.idx_companies if project.idx_companies else [],
            "contributors_count": project.idx_contributors_count
            if project.idx_contributors_count is not None
            else 0,
            "custom_tags": project.idx_custom_tags if project.idx_custom_tags else [],
            "description": project.description if project.description else "",
            "forks_count": project.idx_forks_count if project.idx_forks_count is not None else 0,
            "issues_count": project.idx_issues_count
            if project.idx_issues_count is not None
            else 0,
            "is_active": project.idx_is_active if project.idx_is_active is not None else False,
            "key": project.idx_key if project.idx_key else "",
            "languages": project.idx_languages if project.idx_languages else [],
            "leaders": [leader.name for leader in project.owners.all()] if project.owners else [],
            "level_raw": project.idx_level_raw if project.idx_level_raw is not None else 0.0,
            "level": project.idx_level if project.idx_level else "",
            "name": project.idx_name if project.idx_name else "",
            "organizations": (
                project.idx_organizations
                if isinstance(project.idx_organizations, list)
                else [project.idx_organizations]
            )
            if project.idx_organizations
            else [],
            "repositories": project.idx_repositories if project.idx_repositories else [],
            "repositories_count": project.idx_repositories_count
            if project.idx_repositories_count is not None
            else 0,
            "stars_count": project.stars_count if project.idx_stars_count is not None else 0,
            "summary": project.summary if project.summary else "",
            "tags": project.tags if project.tags else [],
            "topics": project.topics if project.topics else [],
            "type": project.idx_type if project.idx_type else "",
            "top_contributors": [
                {
                    "avatar_url": contributor["avatar_url"],
                    "contributions_count": contributor["contributions_count"],
                    "login": contributor["login"],
                    "name": contributor["name"],
                }
                for contributor in project.idx_top_contributors
            ]
            if project.idx_top_contributors
            else [],
            "updated_at": int(project.idx_updated_at) if project.idx_updated_at else 0,
            "url": project.nest_url if project.nest_url else "",
        }
