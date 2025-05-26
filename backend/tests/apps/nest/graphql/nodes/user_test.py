from apps.nest.graphql.nodes.user import AuthUserNode


def test_auth_user_node_configuration():
    """Test user node configuration."""
    assert AuthUserNode._type_definition.name == "AuthUserNode"

    fields = {f.name: f for f in AuthUserNode._type_definition.fields}
    assert "username" in fields

    username_field = fields["username"]
    assert username_field.type is str or getattr(username_field.type, "of_type", None) is str
