"""Tests for shared GraphQL mutation building blocks."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pydantic
import pytest

from apps.common.api.internal.mutations.common import (
    FieldError,
    pydantic_errors_to_field_errors,
    validate_pydantic_input,
)


class SampleModel(pydantic.BaseModel):
    """Sample pydantic model for validating tests."""

    name: str = pydantic.Field(max_length=5)


@dataclass
class SampleResult:
    """Sample Result class mirroring the mutation Result shape."""

    ok: bool
    code: str | None = None
    message: str | None = None
    field_errors: list[FieldError] | None = None


class TestPydanticErrorsToFieldErrors:
    """Tests for pydantic_errors_to_field_errors."""

    def test_returns_one_entry_per_error(self):
        with pytest.raises(pydantic.ValidationError) as exc_info:
            SampleModel(name="x" * 10)

        result = pydantic_errors_to_field_errors(exc_info.value)

        assert len(result) == 1
        assert result[0].field == "name"
        assert "at most 5 characters" in result[0].message

    def test_joins_nested_loc_with_dot(self):
        class Nested(pydantic.BaseModel):
            inner: SampleModel

        with pytest.raises(pydantic.ValidationError) as exc_info:
            Nested(inner={"name": "x" * 10})

        result = pydantic_errors_to_field_errors(exc_info.value)

        assert result[0].field == "inner.name"


class TestValidatePydanticInput:
    """Tests for validate_pydantic_input decorator."""

    def test_attaches_validated_and_calls_wrapped_on_success(self):
        captured = {}

        @validate_pydantic_input(SampleResult)
        def resolver(self, info, input_data):  # noqa: ARG001
            captured["validated"] = input_data.validated_data
            return SampleResult(ok=True, code="SUCCESS")

        data = MagicMock()
        data.to_pydantic.return_value = SampleModel(name="ok")

        result = resolver(None, MagicMock(), data)

        assert result.ok
        assert result.code == "SUCCESS"
        assert captured["validated"].name == "ok"

    def test_returns_field_errors_on_pydantic_failure(self):
        @validate_pydantic_input(SampleResult)
        def resolver(self, info, input_data):  # noqa: ARG001
            pytest.fail("Resolver body should not run when validation fails.")

        data = MagicMock()
        with pytest.raises(pydantic.ValidationError) as exc_info:
            SampleModel(name="x" * 10)
        data.to_pydantic.side_effect = exc_info.value

        result = resolver(None, MagicMock(), data)

        assert not result.ok
        assert result.code == "VALIDATION_ERROR"
        assert result.message == "Some fields are invalid."
        assert result.field_errors is not None
        assert {fe.field for fe in result.field_errors} == {"name"}

    def test_preserves_wrapped_function_signature_for_introspection(self):
        @validate_pydantic_input(SampleResult)
        def resolver(self, info, input_data: SampleModel) -> SampleResult:  # noqa: ARG001
            """Docstring stays."""
            return SampleResult(ok=True)

        assert resolver.__name__ == "resolver"
        assert resolver.__doc__ == "Docstring stays."
