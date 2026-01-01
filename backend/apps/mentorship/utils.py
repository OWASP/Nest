"""Utility functions for the mentorship app."""


def normalize_name(name):
    """Normalize a string by stripping whitespace and converting to lowercase."""
    return (name or "").strip().casefold()
