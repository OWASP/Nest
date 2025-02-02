import re
from urllib.parse import urlparse

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def is_valid_url(url):
    parsed_url = urlparse(url)

    # A valid URL must have a scheme (http or https) and a netloc (domain)
    if not parsed_url.scheme or not parsed_url.netloc:
        return False

    # valid domain format check
    domain_regex = r"^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9-]{2,}$"
    if not re.match(domain_regex, parsed_url.netloc):
        return False

    return True


def validate_data(schema, data):
    # Perform URL validation before schema validation
    if "downloads" in data:
        invalid_urls = [url for url in data["downloads"] if not is_valid_url(url)]
        if invalid_urls:
            return f"{invalid_urls} has non-uri elements"

    try:
        validate(schema=schema, instance=data)
    except ValidationError as e:
        return e.message
