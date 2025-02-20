"""Schema validator."""

import json
from functools import lru_cache
from pathlib import Path

import validators
from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource

COMMON_JSON = "common.json"

format_checker = FormatChecker()


@format_checker.checks("email")
def check_email_format(value):
    return validators.email(value)


@format_checker.checks("uri")
def check_uri_format(value):
    return validators.url(value)


@lru_cache
def get_registry():
    return Registry().with_resource(
        COMMON_JSON,
        Resource.from_contents(
            json.load(
                Path.open(f"{Path(__file__).parent.parent.resolve()}/{COMMON_JSON}"),
            ),
        ),
    )


def validate_data(schema, data):
    """Validate data against schema."""
    try:
        validate(
            format_checker=format_checker,
            instance=data,
            registry=get_registry(),
            schema=schema,
        )
    except ValidationError as e:
        return e.message
