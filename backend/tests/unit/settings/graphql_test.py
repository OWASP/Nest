"""Tests for GraphQL extension construction and introspection settings."""

from runpy import run_module

import pytest
from strawberry.extensions import DisableIntrospection


@pytest.mark.parametrize(
    ("debug", "is_fuzz_environment", "introspection_disabled"),
    [(False, False, True), (True, False, False), (False, True, False)],
)
def test_graphql_extensions(settings, debug, is_fuzz_environment, introspection_disabled):
    settings.DEBUG = debug
    settings.IS_FUZZ_ENVIRONMENT = is_fuzz_environment
    configured = run_module("settings.graphql")
    schema = configured["schema"]

    assert schema.execute_sync("{ __typename }").errors is None
    result = schema.execute_sync("{ __schema { queryType { name } } }")
    assert bool(result.errors) is introspection_disabled

    if introspection_disabled:
        factory = configured["extensions"][-1]
        first = factory(execution_context=None)
        second = factory(execution_context=None)
        assert isinstance(first, DisableIntrospection)
        assert first is not second
