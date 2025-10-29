import datetime
import uuid

from apps.api.internal.nodes.api_key import ApiKeyNode


class TestApiKeyNode:
    """Test cases for the ApiKeyNode GraphQL type."""

    def test_api_key_node_configuration(self):
        """Tests the configuration of the ApiKeyNode."""
        assert ApiKeyNode.__strawberry_definition__.name == "ApiKeyNode"

        defined_fields = {f.name for f in ApiKeyNode.__strawberry_definition__.fields}

        expected_fields = {
            "_id",
            "created_at",
            "expires_at",
            "is_revoked",
            "name",
            "uuid",
        }

        assert defined_fields == expected_fields

    def test_api_key_node_field_types(self):
        """Tests for ApiKeyNode field types."""
        fields_map = {f.name: f for f in ApiKeyNode.__strawberry_definition__.fields}
        assert fields_map["uuid"].type is uuid.UUID
        assert fields_map["name"].type is str
        assert fields_map["is_revoked"].type is bool
        assert fields_map["created_at"].type is datetime.datetime
        assert fields_map["expires_at"].type is datetime.datetime
