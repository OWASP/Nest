import re
from urllib.parse import urlparse

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def is_valid_url(url):
    parsed_url = urlparse(url)

    if not parsed_url.scheme or not parsed_url.netloc:
        return False

    domain_regex = r"^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9-]{2,}$"
    if not re.match(domain_regex, parsed_url.netloc):
        return False
    return True


def validate_data(schema, data):
    if "demo_url" in data:
        demo_url = data["demo_url"]
        if demo_url == "":
            return "'' is not a 'uri'"
        if demo_url is None:
            return "None is not a 'uri'"
        if demo_url and not is_valid_url(demo_url):
            return f"'{demo_url}' is not a 'uri'"
    try:
        validate(schema=schema, instance=data)
        return None
    except ValidationError as e:
        return e.message
