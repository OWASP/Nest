"""Unit tests for UserBadge model."""

from unittest.mock import Mock, PropertyMock, patch

from apps.nest.models import UserBadge


class TestUserBadgeModel:
    """Unit tests for UserBadge model."""

    def test_str_representation(self):
        """Test __str__ returns user login and badge name."""
        user_badge = UserBadge()

        # Mock the user and badge relationships
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_badge = Mock()
        mock_badge.name = "Contributor"

        # Use PropertyMock to mock the relationships
        with (
            patch.object(type(user_badge), "user", new_callable=PropertyMock) as mock_user_prop,
            patch.object(type(user_badge), "badge", new_callable=PropertyMock) as mock_badge_prop,
        ):
            mock_user_prop.return_value = mock_user
            mock_badge_prop.return_value = mock_badge

            assert str(user_badge) == "testuser - Contributor"

    def test_str_representation_with_different_values(self):
        """Test __str__ with various user and badge combinations."""
        test_cases = [
            ("alice", "OWASP Staff"),
            ("bob123", "Project Leader"),
            ("charlie_dev", "Community Member"),
        ]

        for login, badge_name in test_cases:
            user_badge = UserBadge()
            mock_user = Mock()
            mock_user.login = login
            mock_badge = Mock()
            mock_badge.name = badge_name

            # Use PropertyMock to mock the relationships
            with (
                patch.object(
                    type(user_badge), "user", new_callable=PropertyMock
                ) as mock_user_prop,
                patch.object(
                    type(user_badge), "badge", new_callable=PropertyMock
                ) as mock_badge_prop,
            ):
                mock_user_prop.return_value = mock_user
                mock_badge_prop.return_value = mock_badge

                assert str(user_badge) == f"{login} - {badge_name}"

    def test_bulk_save(self):
        """Test bulk_save calls BulkSaveModel.bulk_save correctly."""
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            user_badges = [Mock(spec=UserBadge), Mock(spec=UserBadge)]
            fields = ["is_active", "awarded_at"]

            UserBadge.bulk_save(user_badges, fields=fields)

            mock_bulk_save.assert_called_once_with(UserBadge, user_badges, fields=fields)

    def test_bulk_save_without_fields(self):
        """Test bulk_save with fields=None."""
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            user_badges = [Mock(spec=UserBadge)]

            UserBadge.bulk_save(user_badges)

            mock_bulk_save.assert_called_once_with(UserBadge, user_badges, fields=None)
