"""Content extractor for Chapter."""

from apps.ai.common.constants import DELIMITER


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

    if chapter.owasp_repository:
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

    if chapter.is_active:
        metadata_parts.append("Active Chapter: Yes")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )
