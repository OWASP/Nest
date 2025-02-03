from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_data(schema, data):
    try:
        validate(schema=schema, instance=data)
    except ValidationError as e:
        return e.message
