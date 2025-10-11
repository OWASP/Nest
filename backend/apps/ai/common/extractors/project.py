"""Content extractor for Project."""

from apps.ai.common.constants import DELIMITER


def extract_project_content(project) -> tuple[str, str]:
    """Extract structured content from project data.

    Args:
        project: Project instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts = []
    metadata_parts = []

    if project.description:
        prose_parts.append(f"Description: {project.description}")

    if project.summary:
        prose_parts.append(f"Summary: {project.summary}")

    if project.owasp_repository:
        repo = project.owasp_repository
        if repo.description:
            prose_parts.append(f"Repository Description: {repo.description}")
        if repo.topics:
            metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

    if project.name:
        metadata_parts.append(f"Project Name: {project.name}")

    if project.level:
        metadata_parts.append(f"Project Level: {project.level}")

    if project.type:
        metadata_parts.append(f"Project Type: {project.type}")

    if project.languages:
        metadata_parts.append(f"Programming Languages: {', '.join(project.languages)}")

    if project.topics:
        metadata_parts.append(f"Topics: {', '.join(project.topics)}")

    if project.licenses:
        metadata_parts.append(f"Licenses: {', '.join(project.licenses)}")

    if project.tags:
        metadata_parts.append(f"Tags: {', '.join(project.tags)}")

    if project.custom_tags:
        metadata_parts.append(f"Custom Tags: {', '.join(project.custom_tags)}")

    stats_parts = []
    if project.stars_count:
        stats_parts.append(f"Stars: {project.stars_count}")
    if project.forks_count:
        stats_parts.append(f"Forks: {project.forks_count}")
    if project.contributors_count:
        stats_parts.append(f"Contributors: {project.contributors_count}")
    if project.releases_count:
        stats_parts.append(f"Releases: {project.releases_count}")
    if project.open_issues_count:
        stats_parts.append(f"Open Issues: {project.open_issues_count}")

    if stats_parts:
        metadata_parts.append("Project Statistics: " + ", ".join(stats_parts))

    if project.leaders_raw:
        metadata_parts.append(f"Project Leaders: {', '.join(project.leaders_raw)}")

    if project.related_urls:
        invalid_urls = getattr(project, "invalid_urls", []) or []
        valid_urls = [url for url in project.related_urls if url and url not in invalid_urls]
        if valid_urls:
            metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

    if project.created_at:
        metadata_parts.append(f"Created: {project.created_at.strftime('%Y-%m-%d')}")

    if project.updated_at:
        metadata_parts.append(f"Last Updated: {project.updated_at.strftime('%Y-%m-%d')}")

    if project.released_at:
        metadata_parts.append(f"Last Release: {project.released_at.strftime('%Y-%m-%d')}")

    if project.health_score is not None:
        metadata_parts.append(f"Health Score: {project.health_score:.2f}")

    metadata_parts.append(f"Active Project: {'Yes' if project.is_active else 'No'}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )
