import re


def is_valid_uri(uri_string):
    """Validate if a string is a valid URI."""
    if not isinstance(uri_string, str):
        return False

    uri_pattern = re.compile(
        r"^(?:http|https|ftp)://"  # protocol
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(uri_pattern.match(uri_string))
