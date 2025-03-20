from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.repository import Repository
from apps.owasp.models.common import RepositoryBasedEntityModel


class EntityModel(RepositoryBasedEntityModel):
    class Meta:
        abstract = False
        app_label = "owasp"


class TestRepositoryBasedEntityModel:
    @pytest.mark.parametrize(
        ("content", "expected_leaders"),
        [
            ("- [Leader1](https://example.com)", ["Leader1"]),
            (
                "* [Leader One (Chapter Lead)](https://example.com)\n"
                "* [Leader Two (Faculty Advisor)](https://example.com)",
                ["Leader One", "Leader Two"],
            ),
            (
                '**<img width = "200" height = "200" src="assets/leader1.jpeg"/>**\n'
                "* [Prof. Leader 1](mailto:leader1@owasp.org) -  Faculty Advisor\n"
                '**<img width = "200" height = "200" src="assets/leader2.jpeg"/>**            \n'
                "* [Leader 2](mailto:leader2@owasp.org)  \n"
                '**<img width = "200" height = "200" src="assets/leader3.jpeg"/>**\n'
                "* [Leader 3](mailto:leader3@owasp.org)\n",
                ["Prof. Leader 1", "Leader 2", "Leader 3"],
            ),
            ("* Leader Two\n* Leader One", ["Leader Two", "Leader One"]),
            ("### Leaders", []),
            ("", []),
            (None, []),
        ],
    )
    def test_get_leaders(self, content, expected_leaders):
        model = EntityModel()
        repository = Repository()
        repository.name = "www-project-example"
        model.owasp_repository = repository

        with patch("apps.owasp.models.common.get_repository_file_content", return_value=content):
            leaders = model.get_leaders()

        assert leaders == expected_leaders

    @pytest.mark.parametrize(
        ("content", "expected_metadata"),
        [
            (
                "\n".join(  # noqa: FLY002
                    (
                        "---",
                        "layout: col-sidebar",
                        "title: OWASP Oklahoma City",
                        "tags: ",
                        "level: 0",
                        "region: North America",
                        "auto-migrated: 0",
                        "meetup-group: Oklahoma-City-Chapter-Meetup",
                        "country: USA",
                        "postal-code: 73101",
                        "---",
                    )
                ),
                {
                    "auto-migrated": 0,
                    "country": "USA",
                    "layout": "col-sidebar",
                    "level": 0,
                    "meetup-group": "Oklahoma-City-Chapter-Meetup",
                    "postal-code": 73101,
                    "region": "North America",
                    "tags": None,
                    "title": "OWASP Oklahoma City",
                },
            ),
        ],
    )
    def test_get_metadata(self, content, expected_metadata):
        model = EntityModel()
        repository = Repository()
        repository.name = "www-project-example"
        model.owasp_repository = repository

        with patch("apps.owasp.models.common.get_repository_file_content", return_value=content):
            metadata = model.get_metadata()

        assert metadata == expected_metadata

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
        ("tags", "expected_tags"),
        [
            ("tag1 tag2 tag3", ["tag1", "tag2", "tag3"]),
            ("tag1, tag2, tag3", ["tag1", "tag2", "tag3"]),
            (["tag1", "tag2", "tag3"], ["tag1", "tag2", "tag3"]),
            ("", []),
            ([], []),
            (None, []),
        ],
    )
    def test_parse_tags(self, tags, expected_tags):
        model = EntityModel()

        with patch(
            "apps.owasp.models.common.get_repository_file_content",
            return_value="---\nfield1: value1\nfield2: value2\n---",
        ):
            tags = model.parse_tags(tags)

        assert tags == expected_tags
