"""Content extractor for Event."""

from apps.ai.common.constants import DELIMITER


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
