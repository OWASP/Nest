import re
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from apps.github.models.repository_contributor import RepositoryContributor


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
        valid_names = [
            "John Doe",
            "Mary Jane Smith",
            "Bob Johnson",
            "Alice Wilson",
            "David Brown",
            "Sarah Miller",
            "Mike Davis",
            "Lisa Garcia",
            "Tom Anderson",
            "Amy Taylor",
            "Chris Martinez",
            "Alex Thompson",
        ]

        regex_pattern = r"\S{2,}\s+\S{2,}"

        for name in valid_names:
            with self.subTest(name=name):
                # Test regex matches
                regex_match = re.search(regex_pattern, name) is not None
                assert regex_match, f"Valid name '{name}' should match regex pattern"

                # Test filter behavior
                with patch(
                    "apps.github.models.repository_contributor.RepositoryContributor.objects"
                ) as mock_objects:
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
                            "user__avatar_url": "https://example.com/avatar.jpg",
                            "total_contributions": 10,
                            "user__login": "testuser",
                            "user__name": name,
                        }
                    ]

                    result = RepositoryContributor.get_top_contributors(has_full_name=True)

                    assert len(result) > 0, (
                        f"Name '{name}' should be included but was filtered out"
                    )
                    assert any(c["name"] == name for c in result), (
                        f"Name '{name}' not found in results"
                    )

    def test_has_full_name_filter_invalid_names(self):
        """Test has_full_name filter with invalid names that should be excluded."""
        invalid_names = [
            "john",
            "A B",
            "X Y Z",
            "",
            "   ",
            "a",
            "J",
            "SingleName",
            "x y",
            "1 2",
            "@ #",
            "AB",
        ]

        regex_pattern = r"\S{2,}\s+\S{2,}"

        for name in invalid_names:
            with self.subTest(name=name):
                # Test regex doesn't match
                regex_match = re.search(regex_pattern, name) is not None
                assert not regex_match, f"Invalid name '{name}' should not match regex pattern"

                # Test filter behavior
                with patch(
                    "apps.github.models.repository_contributor.RepositoryContributor.objects"
                ) as mock_objects:
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
                    assert len(result) == 0, f"Name '{name}' should be excluded but was included"

    def test_has_full_name_filter_multi_word_names(self):
        """Test has_full_name filter with multi-word names (3+ words)."""
        multi_word_names = [
            "John Michael Smith Johnson",
            "Mary Jane Santos Silva",
            "Robert James Wilson Brown",
            "Emily Rose Davis Miller",
            "William Thomas Anderson Lee",
            "Jennifer Anne Thompson White",
            "Michael David Johnson Garcia",
        ]

        for name in multi_word_names:
            with (
                self.subTest(name=name),
                patch(
                    "apps.github.models.repository_contributor.RepositoryContributor.objects"
                ) as mock_objects,
            ):
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
                        "user__avatar_url": "https://example.com/avatar.jpg",
                        "total_contributions": 10,
                        "user__login": "testuser",
                        "user__name": name,
                    }
                ]

                result = RepositoryContributor.get_top_contributors(has_full_name=True)

                # All multi-word names should be included
                assert len(result) > 0, f"Multi-word name '{name}' should be included"
                assert any(c["name"] == name for c in result), (
                    f"Multi-word name '{name}' not found in results"
                )

    def test_has_full_name_filter_short_invalid_names(self):
        """Test has_full_name filter excludes names with parts shorter than 2 characters."""
        short_invalid_names = [
            "A B",
            "X Y",
            "1 2",
            "@ #",
            "a b",
            "J K",
        ]

        regex_pattern = r"\S{2,}\s+\S{2,}"

        for name in short_invalid_names:
            with self.subTest(name=name):
                # Test the actual regex pattern
                match = re.search(regex_pattern, name)

                # These names should NOT match the regex
                assert match is None, f"Name '{name}' should not match regex pattern but it did"

                with patch(
                    "apps.github.models.repository_contributor.RepositoryContributor.objects"
                ) as mock_objects:
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
                    assert len(result) == 0, (
                        f"Invalid name '{name}' should be excluded but was included"
                    )

    def test_has_full_name_filter_disabled_by_default(self):
        """Test that has_full_name filter is not applied when not specified."""
        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects"
        ) as mock_objects:
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
                    "user__avatar_url": "https://example.com/avatar.jpg",
                    "total_contributions": 10,
                    "user__login": "singlename",
                    "user__name": "singlename",
                }
            ]

            # Call without has_full_name parameter
            result = RepositoryContributor.get_top_contributors()

            # Should not call filter with regex (no full name filtering)
            filter_calls = mock_queryset.filter.call_args_list
            regex_calls = [
                call for call in filter_calls if len(call) > 1 and "user__name__regex" in call[1]
            ]
            assert len(regex_calls) == 0, (
                "Should not apply regex filter when has_full_name is not specified"
            )

            assert len(result) > 0, "Should return results when no filtering is applied"

    def test_has_full_name_filter_with_false_value(self):
        """Test that has_full_name=False does not apply the filter."""
        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects"
        ) as mock_objects:
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

            # Call with has_full_name=False
            RepositoryContributor.get_top_contributors(has_full_name=False)

            # Should not call filter with regex
            filter_calls = mock_queryset.filter.call_args_list
            regex_calls = [
                call for call in filter_calls if len(call) > 1 and "user__name__regex" in call[1]
            ]
            assert len(regex_calls) == 0, "Should not apply regex filter when has_full_name=False"
