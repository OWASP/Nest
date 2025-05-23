from apps.nest.graphql.nodes.user import AuthUserNode


def test_auth_user_node_configuration():
    """Test user node configuration."""
    assert AuthUserNode._meta.model.__name__ == "User"
    assert list(AuthUserNode._meta.fields) == ["username"]

    username_field = AuthUserNode._meta.fields["username"]
    assert str(username_field.type) == "String" or str(username_field.type.of_type) == "String"
