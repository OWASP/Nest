from unittest.mock import MagicMock, patch

import pytest

from apps.owasp.models.common import RepositoryBasedEntityModel


class EntityModel(RepositoryBasedEntityModel):
    class Meta:
        abstract = False
        app_label = "test_app"


class TestRepositoryBasedEntityModel:
    @pytest.mark.parametrize(
        ("has_active_repositories", "expected"),
        [
            (True, True),
            (False, False),
        ],
    )
    def test_is_indexable(self, has_active_repositories, expected):
        model = EntityModel()
        model.has_active_repositories = has_active_repositories

        assert model.is_indexable == expected

    @pytest.mark.parametrize(
        ("key", "expected_url"),
        [
            ("example-key", "https://github.com/owasp/example-key"),
            ("another-key", "https://github.com/owasp/another-key"),
        ],
    )
    def test_github_url(self, key, expected_url):
        model = EntityModel()
        model.key = key

        assert model.github_url == expected_url

    @pytest.mark.parametrize(
        ("key", "expected_url"),
        [
            ("example-key", "https://owasp.org/example-key"),
            ("another-key", "https://owasp.org/another-key"),
        ],
    )
    def test_owasp_url(self, key, expected_url):
        model = EntityModel()
        model.key = key

        assert model.owasp_url == expected_url

    def test_deactivate(self):
        model = EntityModel()
        model.is_active = True

        model.save = MagicMock()

        model.deactivate()

        assert model.is_active is False
        model.save.assert_called_once_with(update_fields=("is_active",))

    @pytest.mark.parametrize(
        ("tags", "expected_normalized_tags"),
        [
            ("tag1, tag2, tag3", ["tag1", "tag2", "tag3"]),
            ("tag1 tag2 tag3", ["tag1", "tag2", "tag3"]),
            (["tag1", "tag2", "tag3"], ["tag1", "tag2", "tag3"]),
        ],
    )
    def test_from_github_normalizes_tags(self, tags, expected_normalized_tags):
        model = EntityModel()
        model.tags = tags

        with patch(
            "apps.owasp.models.common.get_repository_file_content",
            return_value="---\nfield1: value1\nfield2: value2\n---",
        ):
            model.from_github({}, None)

        assert model.tags == expected_normalized_tags
