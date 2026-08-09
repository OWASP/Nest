"""Shared GraphQL mutation building blocks."""

import functools
import inspect
from collections.abc import Callable
from typing import Any

import pydantic
import strawberry


@strawberry.type
class FieldError:
    """Per-field validation error."""

    field: str
    message: str


def pydantic_errors_to_field_errors(exc: pydantic.ValidationError) -> list[FieldError]:
    """Convert a Pydantic ValidationError into a list of FieldError.

    Args:
        exc (pydantic.ValidationError): Error raised by to_pydantic().

    Returns:
        list[FieldError]: One entry per validation issue.

    """
    return [
        FieldError(
            field=".".join(str(part) for part in err["loc"]),
            message=err["msg"],
        )
        for err in exc.errors()
    ]


def validate_pydantic_input(
    result_cls: type[Any],
    input_arg: str = "input_data",
) -> Callable:
    """Wrap a mutation resolver with Pydantic input validation.

    Args:
        result_cls (type): The Result GraphQL type used to return validation errors.
        input_arg (str, optional): Name of the resolver's input argument to validate.
            Defaults to "input_data".

    Returns:
        Callable: A decorator that validates the resolver's input.

    """

    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            input_data = bound.arguments[input_arg]
            try:
                object.__setattr__(input_data, "validated_data", input_data.to_pydantic())
            except pydantic.ValidationError as e:
                return result_cls(
                    ok=False,
                    code="VALIDATION_ERROR",
                    message="Some fields are invalid.",
                    field_errors=pydantic_errors_to_field_errors(e),
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
