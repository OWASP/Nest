"""Test cases for ChapterNode."""

from apps.owasp.api.internal.nodes.chapter import ChapterNode


class TestChapterNode:
    def test_chapter_node_inheritance(self):
        assert hasattr(ChapterNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in ChapterNode.__strawberry_definition__.fields}
        expected_field_names = {
            "contribution_data",
            "country",
            "created_at",
            "is_active",
            "name",
            "region",
            "summary",
            "key",
            "geo_location",
            "suggested_location",
            "meetup_group",
            "postal_code",
            "tags",
        }
        assert expected_field_names.issubset(field_names)

    def _get_field_by_name(self, name):
        return next(
            (f for f in ChapterNode.__strawberry_definition__.fields if f.name == name), None
        )

    def test_resolve_key(self):
        field = self._get_field_by_name("key")
        assert field is not None
        assert field.type is str

    def test_resolve_country(self):
        field = self._get_field_by_name("country")
        assert field is not None
        assert field.type is str

    def test_resolve_region(self):
        field = self._get_field_by_name("region")
        assert field is not None
        assert field.type is str

    def test_resolve_is_active(self):
        field = self._get_field_by_name("is_active")
        assert field is not None
        assert field.type is bool

    def test_resolve_contribution_data(self):
        field = self._get_field_by_name("contribution_data")
        assert field is not None
        # contribution_data is a JSON scalar type
