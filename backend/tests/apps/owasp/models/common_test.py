from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.common.utils import clean_url, validate_url
from apps.github.models.repository import Repository
from apps.owasp.models.common import RepositoryBasedEntityModel


class EntityModel(RepositoryBasedEntityModel):
    class Meta:
        abstract = False
        app_label = "owasp"


class TestRepositoryBasedEntityModel:
    def setup_method(self):
        """Set up test fixtures."""
        self.content_type = Mock()
        self.model = EntityModel()
        self.model.id = 1

    @pytest.mark.parametrize(
        ("content", "expected_audience"),
        [
            (
                """### Top Ten Card Game Information
* [Incubator Project](#)
* [Type of Project](#)
* [Version 0.0.0](#)
* [Builder](#)
* [Breaker](#)""",
                ["breaker", "builder"],
            ),
            ("This test contains no audience information.", []),
            ("", []),
            (None, []),
        ],
    )
    def test_get_audience(self, content, expected_audience):
        model = EntityModel()
        repository = Repository()
        repository.name = "www-project-example"
        model.owasp_repository = repository

        with patch("apps.owasp.models.common.get_repository_file_content", return_value=content):
            audience = model.get_audience()

        assert audience == expected_audience

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
        ("content", "expected_leaders"),
        [
            (
                """### Leaders
                    * [First Leader](mailto:first.leader@owasp.org)
                    - Second Leader
                    * [Third Leader](mailto:third.leader@owasp.org)""",
                {
                    "First Leader": "first.leader@owasp.org",
                    "Third Leader": "third.leader@owasp.org",
                },
            ),
            (
                """- [Alice](mailto:alice@example.com)
                    - [Bob](mailto:bob@example.com)""",
                {
                    "Alice": "alice@example.com",
                    "Bob": "bob@example.com",
                },
            ),
            (
                """- [Alice](alice@example.com)
                    - [Bob](bob@example.com)""",
                {
                    "Alice": "alice@example.com",
                    "Bob": "bob@example.com",
                },
            ),
            (
                """- [Alice](mailto:alice@example.com)
                    - [Bob](bob@example.com)
                    - [Charlie](charlie@example.com)""",
                {
                    "Alice": "alice@example.com",
                    "Bob": "bob@example.com",
                    "Charlie": "charlie@example.com",
                },
            ),
            (
                '- <a href="mailto:exmaple@example.com">Leader1</a>',
                {},
            ),
            (
                """## Chapter Leaders
                    Here are the leaders for this chapter:

                    * [Eve](mailto:eve@example.com)
                      - Frank
                    Just some random text here.
                    1. Not a leader list item""",
                {"Eve": "eve@example.com"},
            ),
            (
                """## Chapter Leaders
                    Here are the leaders for this chapter:

                    * [Eve](eve@example.com)
                      - Frank
                    Just some random text here.
                    1. Not a leader list item""",
                {"Eve": "eve@example.com"},
            ),
            (
                "",
                {},
            ),
            (
                None,
                {},
            ),
            (
                "* [  Spaced Leader  ](mailto:  spaced@owasp.org  )",
                {
                    "Spaced Leader": "spaced@owasp.org",
                },
            ),
            (
                "* [  Spaced Leader  ](  spaced@owasp.org  )",
                {
                    "Spaced Leader": "spaced@owasp.org",
                },
            ),
        ],
    )
    def test_get_leaders_emails(self, content, expected_leaders):
        model = EntityModel()
        repository = Repository()
        repository.name = "www-project-example"
        model.owasp_repository = repository

        with patch("apps.owasp.models.common.get_repository_file_content", return_value=content):
            leaders_emails = model.get_leaders_emails()

        assert leaders_emails == expected_leaders

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
        ("content", "domain", "expected_urls"),
        [
            (
                """* [Homepage](https://owasp.org)
* [Project Repo](https://github.com/OWASP/www-project)""",
                None,
                ["https://github.com/OWASP/www-project", "https://owasp.org"],
            ),
            (
                """* [Homepage](https://owasp.org)
* [Project Repo](https://github.com/OWASP/www-project)""",
                "owasp.org",
                ["https://owasp.org"],
            ),
            (
                """* [Homepage](https://owasp.org)""",
                "example.com",
                [],
            ),
            # Test markdown link with self-referencing URL
            (
                """Website: [https://mltop10.info](https://mltop10.info)
Edition: 2023""",
                None,
                ["https://mltop10.info"],
            ),
            # Test mixed content with markdown links and standalone URLs
            (
                """Website: [https://mltop10.info](https://mltop10.info)
[Source Code](https://github.com/OWASP/www-project-machine-learning-security-top-10/tree/master/docs/2023)
([Download PDF](https://mltop10.info/OWASP-Machine-Learning-Security-Top-10.pdf))
Release Notes: https://github.com/OWASP/www-project-machine-learning-security-top-10/releases""",
                None,
                [
                    "https://github.com/OWASP/www-project-machine-learning-security-top-10/releases",
                    "https://github.com/OWASP/www-project-machine-learning-security-top-10/tree/master/docs/2023",
                    "https://mltop10.info",
                    "https://mltop10.info/OWASP-Machine-Learning-Security-Top-10.pdf",
                ],
            ),
            # Test markdown links with text
            (
                """* [Project Homepage](https://example.com)
* [Documentation](https://docs.example.com)""",
                None,
                ["https://docs.example.com", "https://example.com"],
            ),
            # Test URLs with trailing punctuation
            (
                """Check out https://example.com, and also https://test.org!""",
                None,
                ["https://example.com", "https://test.org"],
            ),
            # Test malformed URLs (should be filtered out)
            (
                """* [Broken](https://)
* [Valid](https://example.com)""",
                None,
                ["https://example.com"],
            ),
            # Test empty and None content
            ("This test contains no URLs.", None, []),
            ("", None, []),
            (None, None, []),
        ],
    )
    def test_get_urls(self, content, domain, expected_urls):
        model = EntityModel()
        repository = Repository()
        repository.name = "www-project-example"
        model.owasp_repository = repository

        with patch("apps.owasp.models.common.get_repository_file_content", return_value=content):
            urls = model.get_urls(domain=domain)

        assert urls == expected_urls

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

        assert not model.is_active
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

    @pytest.mark.parametrize(
        ("url", "expected_result"),
        [
            ("https://example.com", "https://example.com"),
            ("https://example.com.", "https://example.com"),
            ("https://example.com,", "https://example.com"),
            ("https://example.com!", "https://example.com"),
            ("https://example.com?", "https://example.com"),
            ("  https://example.com  ", "https://example.com"),
            ("https://", "https://"),
            ("", None),
            (None, None),
            ("not-a-url", "not-a-url"),
            ("ftp://example.com", "ftp://example.com"),
        ],
    )
    def test_clean_url(self, url, expected_result):
        """Test the clean_url helper method."""
        assert clean_url(url) == expected_result

    @pytest.mark.parametrize(
        ("url", "expected_result"),
        [
            ("https://example.com", True),
            ("http://example.com", True),
            ("https://", False),
            ("", False),
            (None, False),
            ("not-a-url", False),
            ("ftp://example.com", False),  # Only http/https allowed
        ],
    )
    def test_validate_url(self, url, expected_result):
        """Test the validate_url helper method."""
        assert validate_url(url) == expected_result

    @patch("apps.owasp.models.common.ContentType")
    @patch("apps.owasp.models.common.EntityMember")
    @patch("apps.owasp.models.common.BulkSaveModel")
    def test_sync_leaders_empty_dict_no_save(
        self, mock_bulk_save, mock_entity_member, mock_content_type
    ):
        """Test sync_leaders with empty dict doesn't call bulk_save."""
        mock_content_type.objects.get_for_model.return_value = self.content_type
        mock_entity_member.objects.filter.return_value = []

        self.model.sync_leaders({})

        mock_bulk_save.bulk_save.assert_not_called()

    @patch("apps.owasp.models.common.ContentType")
    @patch("apps.owasp.models.common.EntityMember")
    @patch("apps.owasp.models.common.BulkSaveModel")
    def test_sync_leaders_mixed_scenario(
        self, mock_bulk_save, mock_entity_member, mock_content_type
    ):
        """Test sync_leaders with both existing and new leaders."""
        mock_content_type.objects.get_for_model.return_value = self.content_type

        existing_leader = Mock()
        existing_leader.member_name = "John Doe"
        existing_leader.member_email = "old@example.com"

        mock_entity_member.objects.filter.return_value = [existing_leader]

        leaders_emails = {
            "John Doe": "new@example.com",  # Update existing
            "Jane Smith": "jane@example.com",  # New leader
        }

        self.model.sync_leaders(leaders_emails)

        call_args = mock_bulk_save.bulk_save.call_args
        leaders_to_save = call_args[0][1]

        assert len(leaders_to_save) == 2  # Updated existing + new leader
