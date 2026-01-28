"""Mentorship API internal utilities."""

import re


def validate_tags(tags: list[str]) -> list[str]:
    """Validate tags for uniqueness and format.

    Args:
        tags: List of tags to validate.

    Returns:
        list[str]: The validated list of tags.

    Raises:
        ValueError: If tags contain duplicates or invalid characters.

    """
    if not tags:
        return []

    if len(tags) != len(set(tags)):
        msg = "Tags must be unique."
        raise ValueError(msg)

    pattern = re.compile(r"^[a-zA-Z0-9]+$")
    for tag in tags:
        if not pattern.match(tag):
            msg = f"Tag '{tag}' must be alphanumeric."
            raise ValueError(msg)

    return tags


def validate_domains(domains: list[str]) -> list[str]:
    """Validate domains for uniqueness and format.

    Args:
        domains: List of domains to validate.

    Returns:
        list[str]: The validated list of domains.

    Raises:
        ValueError: If domains contain duplicates or invalid characters.

    """
    if not domains:
        return []

    if len(domains) != len(set(domains)):
        msg = "Domains must be unique."
        raise ValueError(msg)

    pattern = re.compile(r"^[a-zA-Z0-9 ]+$")
    for domain in domains:
        if not pattern.match(domain):
            msg = f"Domain '{domain}' must be alphanumeric."
            raise ValueError(msg)

    return domains
