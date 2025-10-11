import re
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from apps.github.models.repository_contributor import (
    CONTRIBUTOR_FULL_NAME_REGEX,
    RepositoryContributor,
)

MOCK_AVATAR_URL = "https://example.com/avatar.jpg"
REPOSITORY_CONTRIBUTOR_OBJECTS_PATH = (
    "apps.github.models.repository_contributor.RepositoryContributor.objects"
)


class TestRepositoryContributor(TestCase):
    def test_from_github(self):
        default_contribution_value = 5
        repository_contributor = RepositoryContributor()
        gh_contributions_mock = Mock(contributions=default_contribution_value)
        repository_contributor.from_github(gh_contributions_mock)

        assert repository_contributor.contributions_count == default_contribution_value

    def test_bulk_save(self):
        mock_repository_contributors = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            RepositoryContributor.bulk_save(mock_repository_contributors)
            mock_bulk_save.assert_called_once_with(
                RepositoryContributor, mock_repository_contributors
            )

    def test_update_data(self):
        gh_contributor_mock = MagicMock()
        gh_contributor_mock.raw_data = {"node_id": "12345"}
        repository_mock = MagicMock()
        user_mock = MagicMock()

        mock_repository_contributor = Mock(spec=RepositoryContributor)
        mock_repository_contributor.repository = repository_mock
        mock_repository_contributor.user = user_mock

        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects.get",
            return_value=mock_repository_contributor,
        ):
            repository_contributor = RepositoryContributor()
            repository_contributor.from_github = Mock()

            updated_repository_contributor = RepositoryContributor.update_data(
                gh_contributor_mock, repository_mock, user_mock
            )

            assert (
                updated_repository_contributor.repository == mock_repository_contributor.repository
            )
            assert updated_repository_contributor.user == mock_repository_contributor.user
            assert updated_repository_contributor.from_github.call_count == 1

    def test_has_full_name_filter_valid_names(self):
        """Test has_full_name filter with valid full names that should be included."""
        valid_names = (
            "Alex Thompson",
            "Edwin van der Sar",
            "Marc-André ter Stegen",
            "Mo S. Lo",
            "Mö S. Lö",
            "Mo Sa",
            "Ray W. Johnson",
            "William Thomas Anderson Lee",
        )

        for name in valid_names:
            with self.subTest(name=name):
                # Test regex matches
                regex_match = re.search(CONTRIBUTOR_FULL_NAME_REGEX, name) is not None
                assert regex_match, f"Valid name '{name}' should match regex pattern"

                # Test filter behavior
                with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
                    mock_queryset = MagicMock()
                    qs = mock_objects.by_humans.return_value.to_community_repositories.return_value
                    qs.select_related.return_value = mock_queryset

                    # Mock filter chain
                    mock_queryset.exclude.return_value = mock_queryset
                    mock_queryset.filter.return_value = mock_queryset

                    # Mock aggregation chain
                    mock_values = MagicMock()
                    mock_annotate = MagicMock()
                    mock_order_by = MagicMock()

                    mock_queryset.values.return_value = mock_values
                    mock_values.annotate.return_value = mock_annotate
                    mock_annotate.order_by.return_value = mock_order_by
                    mock_order_by.__getitem__.return_value = [
                        {
                            "total_contributions": 10,
                            "user__avatar_url": MOCK_AVATAR_URL,
                            "user__login": "testuser",
                            "user__name": name,
                            "id": "test-id",
                        }
                    ]

                    result = RepositoryContributor.get_top_contributors(has_full_name=True)

                    assert result, f"Name '{name}' should be included but was filtered out"
                    assert any(c["name"] == name for c in result), (
                        f"Name '{name}' not found in results"
                    )

    def test_has_full_name_filter_invalid_names(self):
        """Test has_full_name filter with invalid names that should be excluded."""
        invalid_names = (
            "   ",
            "",
            "@ #",
            "1 2",
            "a b",
            "A B",
            "a",
            "AB",
            "J K",
            "Jo. Key",
            "john",
            "NoName",
            "NONAME",
            "Single-Name",
            "somethingELSE",
            ". M. S.",
            "X Y Z",
            "x y",
            "X Y",
        )

        for name in invalid_names:
            with self.subTest(name=name):
                # Test regex doesn't match
                regex_match = re.search(CONTRIBUTOR_FULL_NAME_REGEX, name) is not None
                assert not regex_match, f"Invalid name '{name}' should not match regex pattern"

                # Test filter behavior
                with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
                    mock_queryset = MagicMock()
                    qs = mock_objects.by_humans.return_value.to_community_repositories.return_value
                    qs.select_related.return_value = mock_queryset

                    # Mock filter chain
                    mock_queryset.exclude.return_value = mock_queryset
                    mock_queryset.filter.return_value = mock_queryset

                    # Mock aggregation chain
                    mock_values = MagicMock()
                    mock_annotate = MagicMock()
                    mock_order_by = MagicMock()

                    mock_queryset.values.return_value = mock_values
                    mock_values.annotate.return_value = mock_annotate
                    mock_annotate.order_by.return_value = mock_order_by
                    mock_order_by.__getitem__.return_value = []  # No results for invalid names

                    result = RepositoryContributor.get_top_contributors(has_full_name=True)

                    # Should be excluded (empty results)
                    assert not result, f"Name '{name}' should be excluded but was included"

    def test_has_full_name_filter_with_false_value(self):
        """Test that has_full_name=False does not apply the filter."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = MagicMock()
            qs = mock_objects.by_humans.return_value.to_community_repositories.return_value
            qs.select_related.return_value = mock_queryset

            # Mock filter chain
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset

            # Mock aggregation chain
            mock_values = MagicMock()
            mock_annotate = MagicMock()
            mock_order_by = MagicMock()

            mock_queryset.values.return_value = mock_values
            mock_values.annotate.return_value = mock_annotate
            mock_annotate.order_by.return_value = mock_order_by
            mock_order_by.__getitem__.return_value = []

            RepositoryContributor.get_top_contributors(has_full_name=False)

            # Should not call filter with regex
            filter_calls = mock_queryset.filter.call_args_list
            regex_calls = [call for call in filter_calls if "user__name__regex" in call.kwargs]
            assert not regex_calls, "Should not apply regex filter when has_full_name=False"
