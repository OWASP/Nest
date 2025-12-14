import pytest

from apps.slack.common.handlers.users import get_blocks
from apps.slack.common.presentation import EntityPresentation


@pytest.fixture
def mock_users_data():
    return {
        "hits": [
            {
                "idx_name": "John Doe",
                "idx_login": "johndoe",
                "idx_url": "https://github.com/johndoe",
                "idx_bio": "A passionate developer changing the world.",
                "idx_location": "San Francisco",
                "idx_company": "OWASP",
                "idx_followers_count": 100,
                "idx_following_count": 50,
                "idx_public_repositories_count": 10,
            }
        ],
        "nbPages": 3,
    }


class TestGetUsersBlocks:
    def test_get_blocks_no_results(self, mocker):
        """Tests that a "No users found" message is returned when search results are empty."""
        mock_get_users = mocker.patch("apps.github.index.search.user.get_users")
        mock_get_users.return_value = {"hits": [], "nbPages": 0}
        blocks = get_blocks(search_query="nonexistent")
        assert len(blocks) == 1
        assert "No users found for `nonexistent`" in blocks[0]["text"]["text"]

    def test_get_blocks_with_results(self, mocker, mock_users_data):
        """Tests the happy path, ensuring user data is formatted correctly into blocks."""
        mocker.patch("apps.github.index.search.user.get_users", return_value=mock_users_data)
        blocks = get_blocks(search_query="john")
        user_block_text = blocks[1]["text"]["text"]

        assert "OWASP users that I found" in blocks[0]["text"]["text"]
        assert "1. <https://github.com/johndoe|*John Doe*>" in user_block_text
        assert "Company: OWASP" in user_block_text
        assert "Location: San Francisco" in user_block_text
        assert "Followers: 100" in user_block_text
        assert "A passionate developer" in user_block_text

    @pytest.mark.parametrize(
        ("include_pagination", "should_call_pagination"),
        [
            (True, True),
            (False, False),
        ],
    )
    def test_get_blocks_pagination_logic(
        self, mocker, mock_users_data, include_pagination, should_call_pagination
    ):
        mocker.patch("apps.github.index.search.user.get_users", return_value=mock_users_data)
        mock_get_pagination = mocker.patch(
            "apps.slack.common.handlers.users.get_pagination_buttons"
        )
        presentation = EntityPresentation(include_pagination=include_pagination)
        get_blocks(presentation=presentation)
        if should_call_pagination:
            mock_get_pagination.assert_called_once_with("users", 1, 2)
        else:
            mock_get_pagination.assert_not_called()
