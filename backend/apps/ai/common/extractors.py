"""Content extractors for various models."""

from apps.ai.common.constants import DELIMITER


def extract_committee_content(committee) -> tuple[str, str]:
    """Extract structured content from committee data.

    Args:
        committee: Committee instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts = []
    metadata_parts = []

    if committee.description:
        prose_parts.append(f"Description: {committee.description}")

    if committee.summary:
        prose_parts.append(f"Summary: {committee.summary}")

    if hasattr(committee, "owasp_repository") and committee.owasp_repository:
        repo = committee.owasp_repository
        if repo.description:
            prose_parts.append(f"Repository Description: {repo.description}")
        if repo.topics:
            metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

    if committee.name:
        metadata_parts.append(f"Committee Name: {committee.name}")

    if committee.tags:
        metadata_parts.append(f"Tags: {', '.join(committee.tags)}")

    if committee.topics:
        metadata_parts.append(f"Topics: {', '.join(committee.topics)}")

    if committee.leaders_raw:
        metadata_parts.append(f"Committee Leaders: {', '.join(committee.leaders_raw)}")

    if committee.related_urls:
        invalid_urls = getattr(committee, "invalid_urls", []) or []
        valid_urls = [url for url in committee.related_urls if url and url not in invalid_urls]
        if valid_urls:
            metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

    metadata_parts.append(f"Active Committee: {'Yes' if committee.is_active else 'No'}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )


def extract_chapter_content(chapter) -> tuple[str, str]:
    """Extract structured content from chapter data.

    Args:
        chapter: Chapter instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts = []
    metadata_parts = []

    if chapter.description:
        prose_parts.append(f"Description: {chapter.description}")

    if chapter.summary:
        prose_parts.append(f"Summary: {chapter.summary}")

    if hasattr(chapter, "owasp_repository") and chapter.owasp_repository:
        repo = chapter.owasp_repository
        if repo.description:
            prose_parts.append(f"Repository Description: {repo.description}")
        if repo.topics:
            metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

    if chapter.name:
        metadata_parts.append(f"Chapter Name: {chapter.name}")

    location_parts = []
    if chapter.country:
        location_parts.append(f"Country: {chapter.country}")
    if chapter.region:
        location_parts.append(f"Region: {chapter.region}")
    if chapter.postal_code:
        location_parts.append(f"Postal Code: {chapter.postal_code}")
    if chapter.suggested_location:
        location_parts.append(f"Location: {chapter.suggested_location}")

    if location_parts:
        metadata_parts.append(f"Location Information: {', '.join(location_parts)}")

    if chapter.currency:
        metadata_parts.append(f"Currency: {chapter.currency}")

    if chapter.meetup_group:
        metadata_parts.append(f"Meetup Group: {chapter.meetup_group}")

    if chapter.tags:
        metadata_parts.append(f"Tags: {', '.join(chapter.tags)}")

    if chapter.topics:
        metadata_parts.append(f"Topics: {', '.join(chapter.topics)}")

    if chapter.leaders_raw:
        metadata_parts.append(f"Chapter Leaders: {', '.join(chapter.leaders_raw)}")

    if chapter.related_urls:
        invalid_urls = getattr(chapter, "invalid_urls", []) or []
        valid_urls = [url for url in chapter.related_urls if url and url not in invalid_urls]

        if valid_urls:
            metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

    metadata_parts.append(f"Active Chapter: {'Yes' if chapter.is_active else 'No'}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )


def extract_event_content(event) -> tuple[str, str]:
    """Extract structured content from event data.

    Args:
        event: Event instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts = []
    metadata_parts = []

    if event.description:
        prose_parts.append(f"Description: {event.description}")

    if event.summary:
        prose_parts.append(f"Summary: {event.summary}")

    if event.name:
        metadata_parts.append(f"Event Name: {event.name}")

    if event.category:
        metadata_parts.append(f"Category: {event.get_category_display()}")

    if event.start_date:
        metadata_parts.append(f"Start Date: {event.start_date}")

    if event.end_date:
        metadata_parts.append(f"End Date: {event.end_date}")

    if event.suggested_location:
        metadata_parts.append(f"Location: {event.suggested_location}")

    if event.latitude is not None and event.longitude is not None:
        metadata_parts.append(f"Coordinates: {event.latitude}, {event.longitude}")

    if event.url:
        metadata_parts.append(f"Event URL: {event.url}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )


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

    if hasattr(project, "owasp_repository") and project.owasp_repository:
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
    if (project.stars_count or 0) > 0:
        stats_parts.append(f"Stars: {project.stars_count}")
    if (project.forks_count or 0) > 0:
        stats_parts.append(f"Forks: {project.forks_count}")
    if (project.contributors_count or 0) > 0:
        stats_parts.append(f"Contributors: {project.contributors_count}")
    if (project.releases_count or 0) > 0:
        stats_parts.append(f"Releases: {project.releases_count}")
    if (project.open_issues_count or 0) > 0:
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

    metadata_parts.append(f"Issue Tracking: {'Enabled' if project.track_issues else 'Disabled'}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )
