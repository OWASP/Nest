from unittest.mock import patch

import pytest

from apps.slack.common.handlers.users import get_blocks
from apps.slack.common.presentation import EntityPresentation

pagination_buttons_path = "apps.slack.common.handlers.users.get_pagination_buttons"
john_doe = "John Doe"
example_user_url = "https://example.com/user"
dangerous_query = "test & <script>"


class TestUsersHandler:
    @pytest.fixture()
    def mock_user_data(self):
        return {
            "hits": [
                {
                    "idx_name": john_doe,
                    "idx_login": "johndoe",
                    "idx_bio": "This is a test bio",
                    "idx_url": example_user_url,
                    "idx_company": "OWASP",
                    "idx_location": "New York",
                    "idx_followers_count": 100,
                    "idx_following_count": 50,
                    "idx_public_repositories_count": 20,
                    "idx_contributions": 500,
                    "idx_issues_count": 30,
                    "idx_email": "john@example.com",
                    "idx_updated_at": "1704067200",  # 2024-01-01
                }
            ],
            "nbPages": 2,
        }

    @pytest.fixture()
    def mock_empty_user_data(self):
        return {
            "hits": [],
            "nbPages": 0,
        }

    @pytest.fixture()
    def mock_minimal_user_data(self):
        return {
            "hits": [
                {
                    "idx_login": "minimaluser",
                    "idx_url": example_user_url,
                }
            ],
            "nbPages": 1,
        }

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        with patch("apps.github.api.search.user.get_users") as mock_get_users:
            yield {"get_users": mock_get_users}

    def test_get_blocks_with_results(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data

        blocks = get_blocks(search_query="test")

        assert john_doe in blocks[0]["text"]["text"]
        assert "This is a test bio" in blocks[0]["text"]["text"]
        assert "Company: OWASP" in blocks[0]["text"]["text"]
        assert "Location: New York" in blocks[0]["text"]["text"]
        assert "Followers: 100" in blocks[0]["text"]["text"]
        assert "Following: 50" in blocks[0]["text"]["text"]
        assert "Repositories: 20" in blocks[0]["text"]["text"]

    def test_get_blocks_no_results(self, setup_mocks, mock_empty_user_data):
        setup_mocks["get_users"].return_value = mock_empty_user_data

        blocks = get_blocks(search_query="nonexistent")

        assert len(blocks) == 1
        assert "No users found for" in blocks[0]["text"]["text"]

    def test_get_blocks_without_search_query(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data

        blocks = get_blocks()

        assert len(blocks) > 0
        assert john_doe in blocks[0]["text"]["text"]

    def test_get_blocks_no_results_without_query(self, setup_mocks, mock_empty_user_data):
        setup_mocks["get_users"].return_value = mock_empty_user_data

        blocks = get_blocks()

        assert "No users found" in blocks[0]["text"]["text"]
        assert "`" not in blocks[0]["text"]["text"]

    def test_minimal_user_data(self, setup_mocks, mock_minimal_user_data):
        setup_mocks["get_users"].return_value = mock_minimal_user_data
        presentation = EntityPresentation(include_metadata=True)

        blocks = get_blocks(presentation=presentation)

        assert "minimaluser" in blocks[0]["text"]["text"]
        assert "_" in blocks[0]["text"]["text"]
        assert "Company:" not in blocks[0]["text"]["text"]
        assert "Location:" not in blocks[0]["text"]["text"]
        assert "Followers:" not in blocks[0]["text"]["text"]

    def test_feedback_message(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_feedback=True)

        blocks = get_blocks(presentation=presentation)

        assert "Extended search over OWASP community users" in blocks[-1]["text"]["text"]

    def test_pagination(self, setup_mocks, mock_user_data):
        mock_user_data["nbPages"] = 3
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(pagination_buttons_path) as mock_pagination:
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}}
            ]
            blocks = get_blocks(page=1, presentation=presentation)
            assert mock_pagination.called
            assert blocks[-1]["type"] == "actions"

            expected_button_count = 2
            mock_pagination.return_value = [
                {"type": "button", "text": {"type": "plain_text", "text": "Previous"}},
                {"type": "button", "text": {"type": "plain_text", "text": "Next"}},
            ]
            blocks = get_blocks(page=2, presentation=presentation)
            assert len(blocks[-1]["elements"]) == expected_button_count
            assert mock_pagination.call_count == expected_button_count

    def test_no_pagination_when_disabled(self, setup_mocks, mock_user_data):
        mock_user_data["nbPages"] = 3
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_pagination=False)

        blocks = get_blocks(presentation=presentation)
        assert len(blocks) > 0
        assert all(block["type"] != "actions" for block in blocks)

    def test_variable_metadata_combinations(self, setup_mocks):
        test_cases = [
            {
                "idx_login": "user1",
                "idx_name": "User One",
                "idx_company": "Company",
                "idx_location": "",
                "idx_followers_count": 0,
                "idx_following_count": 0,
                "idx_public_repositories_count": 0,
            },
            {
                "idx_login": "user2",
                "idx_name": "",
                "idx_company": "",
                "idx_location": "Location",
                "idx_followers_count": 10,
                "idx_following_count": 0,
                "idx_public_repositories_count": 0,
            },
            {
                "idx_login": "user3",
                "idx_name": "",
                "idx_company": "",
                "idx_location": "",
                "idx_followers_count": 0,
                "idx_following_count": 20,
                "idx_public_repositories_count": 0,
            },
            {
                "idx_login": "user4",
                "idx_name": "",
                "idx_company": "",
                "idx_location": "",
                "idx_followers_count": 0,
                "idx_following_count": 0,
                "idx_public_repositories_count": 30,
            },
        ]

        for case in test_cases:
            mock_data = {
                "hits": [{"idx_url": example_user_url, "idx_bio": "Bio text", **case}],
                "nbPages": 1,
            }
            setup_mocks["get_users"].return_value = mock_data

            blocks = get_blocks(presentation=EntityPresentation(include_metadata=True))

            user_name = case.get("idx_name") or case.get("idx_login")
            assert user_name in blocks[0]["text"]["text"]

            metadata_checks = [
                ("Company:", case["idx_company"]),
                ("Location:", case["idx_location"]),
                ("Followers:", case["idx_followers_count"]),
                ("Following:", case["idx_following_count"]),
                ("Repositories:", case["idx_public_repositories_count"]),
            ]

            for label, value in metadata_checks:
                if value:
                    assert f"{label} {value}" in blocks[0]["text"]["text"]
                else:
                    assert label not in blocks[0]["text"]["text"]

    def test_no_bio(self, setup_mocks, mock_user_data):
        mock_user_data["hits"][0]["idx_bio"] = ""
        setup_mocks["get_users"].return_value = mock_user_data

        blocks = get_blocks()
        assert "_" in blocks[0]["text"]["text"]

    def test_search_query_escaping(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data

        presentation = EntityPresentation(include_feedback=True)
        blocks = get_blocks(search_query=dangerous_query, presentation=presentation)

        blocks_str = str(blocks)
        assert dangerous_query in blocks_str
        html_content = blocks[0]["text"]["text"]
        assert "&amp;" in html_content
        assert "&lt;script&gt;" in html_content
        assert "community/users?q=test & <script>" in blocks_str

    def test_pagination_edge_case(self, setup_mocks, mock_user_data):
        mock_user_data["nbPages"] = 2
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_pagination=True)

        with patch(pagination_buttons_path) as mock_pagination:
            mock_pagination.return_value = None
            blocks = get_blocks(page=2, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)
            assert mock_pagination.called

    def test_empty_blocks_initialization(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data

        blocks = get_blocks()

        assert isinstance(blocks, list)
        assert len(blocks) > 0
        assert all(isinstance(block, dict) for block in blocks)
