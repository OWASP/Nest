from jsonschema import validate, FormatChecker
from jsonschema.exceptions import ValidationError
import validators


def validate_data(schema, data):
    """Validate data against schema."""
    format_checker = FormatChecker()

    @format_checker.checks("uri")
    def check_uri_format(value):
        return validators.url(value)

    try:
        validate(schema=schema, instance=data, format_checker=format_checker)
    except ValidationError as e:
        return e.message
