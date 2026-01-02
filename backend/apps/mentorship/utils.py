"""Utility functions for the mentorship app."""


def normalize_name(name: str | None) -> str:
    """Normalize a string by stripping whitespace and converting to lowercase.
    
    Args:
        name (str, optional): The name string to normalize.
        
    Returns:
        str: The normalized name string (lowercase with whitespace stripped).
    
    """
    return (name or "").strip().casefold()
