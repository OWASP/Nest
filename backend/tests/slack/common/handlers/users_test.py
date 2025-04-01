from unittest.mock import patch

import pytest

from apps.slack.common.handlers.users import get_blocks
from apps.slack.common.presentation import EntityPresentation


class TestUsersHandler:
    @pytest.fixture()
    def mock_user_data(self):
        return {
            "hits": [
                {
                    "idx_name": "John Doe",
                    "idx_login": "johndoe",
                    "idx_bio": "This is a test bio",
                    "idx_url": "https://example.com/user",
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
                    "idx_url": "https://example.com/user",
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

        assert "John Doe" in blocks[0]["text"]["text"]
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
        assert "John Doe" in blocks[0]["text"]["text"]

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

        with patch("apps.slack.common.handlers.users.get_pagination_buttons") as mock_pagination:
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
                "hits": [{"idx_url": "https://example.com/user", "idx_bio": "Bio text", **case}],
                "nbPages": 1,
            }
            setup_mocks["get_users"].return_value = mock_data

            blocks = get_blocks(presentation=EntityPresentation(include_metadata=True))

            user_name = case.get("idx_name") or case.get("idx_login")
            assert user_name in blocks[0]["text"]["text"]

            if case["idx_company"]:
                assert f"Company: {case['idx_company']}" in blocks[0]["text"]["text"]
            else:
                assert "Company:" not in blocks[0]["text"]["text"]

            if case["idx_location"]:
                assert f"Location: {case['idx_location']}" in blocks[0]["text"]["text"]
            else:
                assert "Location:" not in blocks[0]["text"]["text"]

            if case["idx_followers_count"]:
                assert f"Followers: {case['idx_followers_count']}" in blocks[0]["text"]["text"]
            else:
                assert "Followers:" not in blocks[0]["text"]["text"]

            if case["idx_following_count"]:
                assert f"Following: {case['idx_following_count']}" in blocks[0]["text"]["text"]
            else:
                assert "Following:" not in blocks[0]["text"]["text"]

            if case["idx_public_repositories_count"]:
                assert (
                    f"Repositories: {case['idx_public_repositories_count']}"
                    in blocks[0]["text"]["text"]
                )
            else:
                assert "Repositories:" not in blocks[0]["text"]["text"]

    def test_no_bio(self, setup_mocks, mock_user_data):
        mock_user_data["hits"][0]["idx_bio"] = ""
        setup_mocks["get_users"].return_value = mock_user_data

        blocks = get_blocks()
        assert "_" in blocks[0]["text"]["text"]

    def test_search_query_escaping(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data
        dangerous_query = "test & <script>"

        presentation = EntityPresentation(include_feedback=True)
        blocks = get_blocks(search_query=dangerous_query, presentation=presentation)

        blocks_str = str(blocks)
        assert dangerous_query in blocks_str

        assert "community/users?q=test & <script>" in blocks_str

    def test_pagination_empty(self, setup_mocks, mock_user_data):
        mock_user_data["nbPages"] = 1
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_pagination=True)

        with patch("apps.slack.common.handlers.users.get_pagination_buttons", return_value=[]):
            blocks = get_blocks(page=1, presentation=presentation)
            assert all(block["type"] != "actions" for block in blocks)

    def test_blocks_initialization(self, setup_mocks, mock_user_data):
        setup_mocks["get_users"].return_value = mock_user_data
        search_query = "test"

        blocks = get_blocks(search_query=search_query)

        assert len(blocks) > 0
        assert blocks[0]["type"] == "section"
        assert "John Doe" in blocks[0]["text"]["text"]

    def test_pagination_edge_case(self, setup_mocks, mock_user_data):
        mock_user_data["nbPages"] = 2
        setup_mocks["get_users"].return_value = mock_user_data
        presentation = EntityPresentation(include_pagination=True)

        with patch("apps.slack.common.handlers.users.get_pagination_buttons") as mock_pagination:
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
