"""Common app utils."""


def join_values(fields, delimiter=" "):
    """Join non-empty field values using the delimiter."""
    delimiter.join(field for field in fields if field)
