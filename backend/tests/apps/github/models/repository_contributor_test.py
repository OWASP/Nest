import re
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from apps.github.models.repository import Repository
from apps.github.models.repository_contributor import (
    CONTRIBUTOR_FULL_NAME_REGEX,
    RepositoryContributor,
)
from apps.github.models.user import User

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

    def test_from_github_with_none_values(self):
        """Test that from_github handles None values gracefully."""
        repository_contributor = RepositoryContributor(contributions_count=5)
        gh_contributions_mock = Mock(contributions=None)
        repository_contributor.from_github(gh_contributions_mock)

        assert repository_contributor.contributions_count == 5

    def test_bulk_save(self):
        mock_repository_contributors = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            RepositoryContributor.bulk_save(mock_repository_contributors)
            mock_bulk_save.assert_called_once_with(
                RepositoryContributor, mock_repository_contributors
            )

    def test_str(self):
        """Test the __str__ method."""
        user = MagicMock(spec=User, _state=Mock(db=None))
        user.__str__.return_value = "testuser"
        repository = MagicMock(spec=Repository, _state=Mock(db=None))
        repository.__str__.return_value = "test_repository"
        contributor = RepositoryContributor(
            user=user, repository=repository, contributions_count=10
        )
        expected_str = "testuser has made 10 contributions to test_repository"
        assert str(contributor) == expected_str

    def test_str_zero_contributions(self):
        """Test the __str__ method for zero contributions."""
        user = MagicMock(spec=User, _state=Mock(db=None))
        user.__str__.return_value = "testuser"
        repository = MagicMock(spec=Repository, _state=Mock(db=None))
        repository.__str__.return_value = "test_repository"
        contributor = RepositoryContributor(
            user=user, repository=repository, contributions_count=0
        )
        expected_str = "testuser has made 0 contributions to test_repository"
        assert str(contributor) == expected_str

    def test_update_data_existing(self):
        """Test update_data for an existing contributor."""
        gh_contributor_mock = Mock(contributions=20)
        repository_mock = Mock(spec=Repository, _state=Mock(db=None))
        user_mock = Mock(spec=User, _state=Mock(db=None))
        existing_contributor = Mock(spec=RepositoryContributor)

        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects.get",
            return_value=existing_contributor,
        ) as mock_get:
            contributor = RepositoryContributor.update_data(
                gh_contributor_mock, repository_mock, user_mock
            )

            mock_get.assert_called_once_with(repository=repository_mock, user=user_mock)
            existing_contributor.from_github.assert_called_once_with(gh_contributor_mock)
            existing_contributor.save.assert_called_once()
            assert contributor == existing_contributor

    def test_update_data_creates_new(self):
        """Test update_data creates a new contributor if one does not exist."""
        gh_contributor_mock = Mock(contributions=15)
        repository_mock = Mock(spec=Repository, _state=Mock(db=None))
        user_mock = Mock(spec=User, _state=Mock(db=None))

        with (
            patch(
                "apps.github.models.repository_contributor.RepositoryContributor.objects.get",
                side_effect=RepositoryContributor.DoesNotExist,
            ) as mock_get,
            patch(
                "apps.github.models.repository_contributor.RepositoryContributor.save",
            ) as mock_save,
        ):
            contributor = RepositoryContributor.update_data(
                gh_contributor_mock, repository_mock, user_mock
            )

            mock_get.assert_called_once_with(repository=repository_mock, user=user_mock)
            assert contributor.repository == repository_mock
            assert contributor.user == user_mock
            assert contributor.contributions_count == 15
            mock_save.assert_called_once()

    def test_str_singular(self):
        """Test the __str__ method for a single contribution."""
        user = MagicMock(spec=User, _state=Mock(db=None))
        user.__str__.return_value = "testuser"
        repository = MagicMock(spec=Repository, _state=Mock(db=None))
        repository.__str__.return_value = "test_repository"
        contributor = RepositoryContributor(
            user=user, repository=repository, contributions_count=1
        )
        expected_str = "testuser has made 1 contribution to test_repository"
        assert str(contributor) == expected_str

    def test_update_data_no_save(self):
        """Test update_data with save=False."""
        gh_contributor_mock = Mock(contributions=20)
        repository_mock = Mock(spec=Repository, _state=Mock(db=None))
        user_mock = Mock(spec=User, _state=Mock(db=None))
        existing_contributor = Mock(spec=RepositoryContributor)

        with patch(
            "apps.github.models.repository_contributor.RepositoryContributor.objects.get",
            return_value=existing_contributor,
        ) as mock_get:
            RepositoryContributor.update_data(
                gh_contributor_mock, repository_mock, user_mock, save=False
            )
            mock_get.assert_called_once_with(repository=repository_mock, user=user_mock)
            existing_contributor.from_github.assert_called_once_with(gh_contributor_mock)
            assert existing_contributor.save.call_count == 0

    def _setup_mock_queryset(self, mock_objects):
        mock_queryset = MagicMock()
        qs = mock_objects.by_humans.return_value.to_community_repositories.return_value
        qs.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.exclude.return_value = mock_queryset
        (
            mock_queryset.values.return_value.annotate.return_value.order_by.return_value.__getitem__.return_value
        ) = []
        return mock_queryset

    def test_get_top_contributors_project_filter(self):
        """Test the project filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors(project="my-project")
            mock_queryset.filter.assert_any_call(
                repository__project__key__iexact="www-project-my-project"
            )

    def test_get_top_contributors_chapter_filter(self):
        """Test the chapter filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors(chapter="my-chapter")
            mock_queryset.filter.assert_any_call(repository__key__iexact="www-chapter-my-chapter")

    def test_get_top_contributors_committee_filter(self):
        """Test the committee filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors(committee="my-committee")
            mock_queryset.filter.assert_any_call(
                repository__key__iexact="www-committee-my-committee"
            )

    def test_get_top_contributors_repository_filter(self):
        """Test the repository filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors(repository="my-repo")
            mock_queryset.filter.assert_any_call(repository__name__iexact="my-repo")

    def test_get_top_contributors_excluded_usernames_filter(self):
        """Test the excluded_usernames filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors(excluded_usernames=["user1"])
            mock_queryset.exclude.assert_called_once_with(user__login__in=["user1"])

    def test_get_top_contributors_project_contributors_filter(self):
        """Test the project contributors filter for main pages."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)
            RepositoryContributor.get_top_contributors()
            mock_queryset.filter.assert_called_with(repository__project__isnull=False)

    def test_get_top_contributors_data_processing(self):
        """Test that get_top_contributors correctly processes and returns data."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = MagicMock()
            qs = mock_objects.by_humans.return_value.to_community_repositories.return_value
            qs.select_related.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset

            (
                mock_queryset.values.return_value.annotate.return_value.order_by.return_value.__getitem__
            ).return_value = [
                {
                    "user__avatar_url": "url1",
                    "user__login": "user1",
                    "user__name": "User One",
                    "total_contributions": 100,
                },
            ]

            result = RepositoryContributor.get_top_contributors()
            expected = [
                {
                    "avatar_url": "url1",
                    "contributions_count": 100,
                    "id": "user1",
                    "login": "user1",
                    "name": "User One",
                }
            ]
            assert result == expected

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

    def test_get_top_contributors_organization_filter(self):
        """Test the organization filtering logic in get_top_contributors."""
        with patch(REPOSITORY_CONTRIBUTOR_OBJECTS_PATH) as mock_objects:
            mock_queryset = self._setup_mock_queryset(mock_objects)

            # Mock the select_related to return a queryset that tracks filter calls
            mock_after_select = MagicMock()
            mock_queryset.select_related.return_value = mock_after_select
            mock_after_select.filter.return_value = mock_queryset

            RepositoryContributor.get_top_contributors(organization="test-org")
            # Check that select_related and filter were called with organization
            mock_queryset.select_related.assert_called_with("repository__organization")
            mock_after_select.filter.assert_called_once_with(
                repository__organization__login="test-org"
            )
