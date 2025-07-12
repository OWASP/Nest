import datetime

import strawberry

from apps.nest.graphql.nodes.api_key import APIKeyNode


class TestAPIKeyNode:
    """Test cases for the APIKeyNode GraphQL type."""

    def test_api_key_node_configuration(self):
        """Tests the configuration of the APIKeyNode."""
        assert APIKeyNode.__strawberry_definition__.name == "APIKeyNode"

        defined_fields = {f.name for f in APIKeyNode.__strawberry_definition__.fields}

        expected_fields = {
            "id",
            "name",
            "is_revoked",
            "created_at",
            "expires_at",
            "key_suffix",
        }

        assert defined_fields == expected_fields

    def test_api_key_node_field_types(self):
        """Tests for APIKeyNode field types."""
        fields_map = {f.name: f for f in APIKeyNode.__strawberry_definition__.fields}

        assert fields_map["id"].type is strawberry.ID
        assert fields_map["name"].type is str
        assert fields_map["is_revoked"].type is bool
        assert fields_map["key_suffix"].type is str
        assert fields_map["created_at"].type is datetime.datetime
        assert fields_map["expires_at"].type.of_type is datetime.datetime
