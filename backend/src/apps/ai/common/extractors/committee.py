"""Context extractor for Committee."""

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

    if committee.owasp_repository:
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
