from unittest.mock import MagicMock, patch

import pytest

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.mentee import MenteeNode
from apps.mentorship.api.internal.queries.mentorship import MentorshipQuery
from apps.mentorship.models import Mentee, Module


@pytest.fixture
def api_mentorship_queries() -> MentorshipQuery:
    """Pytest fixture to return an instance of the query resolver class."""
    return MentorshipQuery()


class TestIsMentor:
    """Tests for the is_mentor query."""

    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.get")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentor.objects.filter")
    def test_is_mentor_true(
        self,
        mock_mentor_filter: MagicMock,
        mock_github_user_get: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test that is_mentor returns True when the user is a mentor."""
        mock_github_user_get.return_value = MagicMock(spec=GithubUser)
        mock_mentor_filter.return_value.exists.return_value = True

        is_mentor = api_mentorship_queries.is_mentor
        result = is_mentor(login="testuser")

        assert result
        mock_github_user_get.assert_called_once_with(login="testuser")
        mock_mentor_filter.assert_called_once()
        mock_mentor_filter.return_value.exists.assert_called_once()

    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.get")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentor.objects.filter")
    def test_is_mentor_false_not_mentor(
        self,
        mock_mentor_filter: MagicMock,
        mock_github_user_get: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test that is_mentor returns False when the user is not a mentor."""
        mock_github_user_get.return_value = MagicMock(spec=GithubUser)
        mock_mentor_filter.return_value.exists.return_value = False

        is_mentor = api_mentorship_queries.is_mentor
        result = is_mentor(login="testuser")

        assert not result
        mock_github_user_get.assert_called_once_with(login="testuser")
        mock_mentor_filter.assert_called_once()
        mock_mentor_filter.return_value.exists.assert_called_once()

    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.get")
    def test_is_mentor_false_no_github_user(
        self, mock_github_user_get: MagicMock, api_mentorship_queries
    ) -> None:
        """Test that is_mentor returns False when the GitHub user does not exist."""
        mock_github_user_get.side_effect = GithubUser.DoesNotExist

        is_mentor = api_mentorship_queries.is_mentor
        result = is_mentor(login="non_existent_user")

        assert not result
        mock_github_user_get.assert_called_once_with(login="non_existent_user")

    @pytest.mark.parametrize("login", ["", "   ", None])
    def test_is_mentor_false_empty_login(self, login: str | None, api_mentorship_queries) -> None:
        """Test that is_mentor returns False for empty or whitespace login."""
        is_mentor = api_mentorship_queries.is_mentor
        result = is_mentor(login=login)

        assert not result


class TestGetMenteeDetails:
    """Tests for the get_mentee_details query."""

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_details_success(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test successful retrieval of mentee details."""
        mock_module = MagicMock(spec=Module)
        mock_module.id = 1
        mock_module_only.return_value.get.return_value = mock_module

        mock_github_user = MagicMock(spec=GithubUser)
        mock_github_user.login = "test_mentee"
        mock_github_user.name = "Test_Mentee"
        mock_github_user.avatar_url = "url"
        mock_github_user.bio = "bio"

        mock_github_user_only.return_value.get.return_value = mock_github_user

        mock_mentee = MagicMock(spec=Mentee)
        mock_mentee.id = 2
        mock_mentee.experience_level = "Mid"
        mock_mentee.domains = ["Web"]
        mock_mentee.tags = ["Python"]
        mock_mentee_only.return_value.get.return_value = mock_mentee

        mock_mentee_module_filter.return_value.exists.return_value = True

        get_mentee_details = api_mentorship_queries.get_mentee_details
        result = get_mentee_details(
            program_key="program", module_key="module", mentee_key="test_mentee"
        )

        assert isinstance(result, MenteeNode)
        assert result.login == "test_mentee"
        assert result.name == "Test_Mentee"
        assert result.experience_level == "Mid"
        assert "Python" in result.tags

        mock_module_only.assert_called_once_with("id")
        mock_module_only.return_value.get.assert_called_once_with(
            key="module", program__key="program"
        )
        mock_github_user_only.assert_called_once_with("login", "name", "avatar_url", "bio")
        mock_github_user_only.return_value.get.assert_called_once_with(login="test_mentee")
        mock_mentee_only.assert_called_once_with("id", "experience_level", "domains", "tags")
        mock_mentee_only.return_value.get.assert_called_once_with(github_user=mock_github_user)
        mock_mentee_module_filter.assert_called_once_with(mentee=mock_mentee, module=mock_module)
        mock_mentee_module_filter.return_value.exists.assert_called_once()

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    def test_get_mentee_details_module_does_not_exist(
        self, mock_module_only: MagicMock, api_mentorship_queries
    ) -> None:
        """Test when the module does not exist."""
        mock_module_only.return_value.get.side_effect = Module.DoesNotExist

        get_mentee_details = api_mentorship_queries.get_mentee_details
        result = get_mentee_details(
            program_key="program", module_key="nonexistent", mentee_key="test_mentee"
        )
        assert result is None

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    def test_get_mentee_details_github_user_does_not_exist(
        self, mock_github_user_only: MagicMock, mock_module_only: MagicMock, api_mentorship_queries
    ) -> None:
        """Test when the GitHub user does not exist."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.side_effect = GithubUser.DoesNotExist

        get_mentee_details = api_mentorship_queries.get_mentee_details
        result = get_mentee_details(
            program_key="program", module_key="module", mentee_key="nonexistent"
        )
        assert result is None

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    def test_get_mentee_details_mentee_does_not_exist(
        self,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test when the mentee does not exist."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.return_value = MagicMock(
            spec=GithubUser, login="test_mentee"
        )
        mock_mentee_only.return_value.get.side_effect = Mentee.DoesNotExist

        get_mentee_details = api_mentorship_queries.get_mentee_details
        result = get_mentee_details(
            program_key="program", module_key="module", mentee_key="test_mentee"
        )
        assert result is None

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_details_not_enrolled(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test when the mentee is not enrolled in the module."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.return_value = MagicMock(
            spec=GithubUser, login="test_mentee"
        )
        mock_mentee_only.return_value.get.return_value = MagicMock(spec=Mentee, id=2)
        mock_mentee_module_filter.return_value.exists.return_value = False

        get_mentee_details = api_mentorship_queries.get_mentee_details
        result = get_mentee_details(
            program_key="program", module_key="module", mentee_key="test_mentee"
        )
        assert result is None


class TestGetMenteeModuleIssues:
    """Tests for the get_mentee_module_issues query."""

    @patch("apps.mentorship.api.internal.queries.mentorship.Prefetch")
    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_module_issues_success(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        mock_prefetch: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test successful retrieval of mentee module issues."""
        mock_prefetch.return_value = MagicMock()
        mock_module = MagicMock(spec=Module, id=1)
        mock_module_only.return_value.get.return_value = mock_module

        mock_github_user = MagicMock(spec=GithubUser, id=1, login="test_mentee")
        mock_github_user_only.return_value.get.return_value = mock_github_user

        mock_mentee = MagicMock(spec=Mentee, id=2)
        mock_mentee_only.return_value.get.return_value = mock_mentee

        mock_mentee_module_filter.return_value.exists.return_value = True

        mock_issue1 = MagicMock(
            id=1, number=1, title="Issue 1", state="open", created_at="", url=""
        )
        mock_issue2 = MagicMock(
            id=2, number=2, title="Issue 2", state="closed", created_at="", url=""
        )

        mock_issues_qs = MagicMock()
        mock_issues_qs.__getitem__.return_value = [mock_issue1, mock_issue2]

        mock_module_filter = (
            mock_module.issues.filter.return_value.only.return_value.prefetch_related
        )
        mock_module_filter.return_value.order_by.return_value = mock_issues_qs

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program", module_key="module", mentee_key="test_mentee"
        )

        assert len(result) == 2
        assert result[0].title == "Issue 1"
        assert result[1].title == "Issue 2"

        mock_module_only.assert_called_once_with("id")
        mock_module_only.return_value.get.assert_called_once_with(
            key="module", program__key="program"
        )
        mock_github_user_only.return_value.get.assert_called_once_with(login="test_mentee")
        mock_mentee_only.assert_called_once_with("id")
        mock_mentee_only.return_value.get.assert_called_once_with(github_user=mock_github_user)
        mock_mentee_module_filter.assert_called_once_with(mentee=mock_mentee, module=mock_module)
        mock_mentee_module_filter.return_value.exists.assert_called_once()
        mock_module.issues.filter.assert_called_once_with(assignees=mock_github_user)

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    def test_get_mentee_module_issues_module_does_not_exist(
        self, mock_module_only: MagicMock, api_mentorship_queries
    ) -> None:
        """Test when the module does not exist."""
        mock_module_only.return_value.get.side_effect = Module.DoesNotExist

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program", module_key="nonexistent", mentee_key="test_mentee"
        )
        assert result == []

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    def test_get_mentee_module_issues_github_user_does_not_exist(
        self, mock_github_user_only: MagicMock, mock_module_only: MagicMock, api_mentorship_queries
    ) -> None:
        """Test when the GitHub user does not exist."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.side_effect = GithubUser.DoesNotExist

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program", module_key="module", mentee_key="nonexistent"
        )
        assert result == []

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    def test_get_mentee_module_issues_mentee_does_not_exist(
        self,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test when the mentee does not exist."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.return_value = MagicMock(
            spec=GithubUser, login="test_mentee"
        )
        mock_mentee_only.return_value.get.side_effect = Mentee.DoesNotExist

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program", module_key="module", mentee_key="nonexistent"
        )
        assert result == []

    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_module_issues_not_enrolled(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test when the mentee is not enrolled in the module."""
        mock_module_only.return_value.get.return_value = MagicMock(spec=Module, id=1)
        mock_github_user_only.return_value.get.return_value = MagicMock(
            spec=GithubUser, login="test_mentee"
        )
        mock_mentee_only.return_value.get.return_value = MagicMock(spec=Mentee, id=2)
        mock_mentee_module_filter.return_value.exists.return_value = False

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program", module_key="module", mentee_key="nonexistent"
        )
        assert result == []

    @patch("apps.mentorship.api.internal.queries.mentorship.Prefetch")
    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_module_issues_pagination(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        mock_prefetch: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """Test pagination for mentee module issues."""
        mock_prefetch.return_value = MagicMock()
        mock_module = MagicMock(spec=Module, id=1)
        mock_module_only.return_value.get.return_value = mock_module

        mock_github_user = MagicMock(spec=GithubUser, id=1, login="test_mentee")
        mock_github_user_only.return_value.get.return_value = mock_github_user

        mock_mentee = MagicMock(spec=Mentee, id=2)
        mock_mentee_only.return_value.get.return_value = mock_mentee

        mock_mentee_module_filter.return_value.exists.return_value = True

        mock_issue2 = MagicMock(
            id=2, number=2, title="Issue 2", state="closed", created_at="", url=""
        )

        mock_issues_qs_slice = [mock_issue2]

        mock_issues_qs = MagicMock()
        mock_issues_qs.__getitem__.return_value = mock_issues_qs_slice

        mock_module_filter = (
            mock_module.issues.filter.return_value.only.return_value.prefetch_related
        )
        mock_module_filter.return_value.order_by.return_value = mock_issues_qs

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program",
            module_key="module",
            mentee_key="test_mentee",
            limit=1,
            offset=1,
        )

        assert len(result) == 1
        assert result[0].title == "Issue 2"

        mock_module.issues.filter.assert_called_once_with(assignees=mock_github_user)

    @patch("apps.mentorship.api.internal.queries.mentorship.Prefetch")
    @patch("apps.mentorship.api.internal.queries.mentorship.Module.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.GithubUser.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.Mentee.objects.only")
    @patch("apps.mentorship.api.internal.queries.mentorship.MenteeModule.objects.filter")
    def test_get_mentee_module_issues_pagination_out_of_range(
        self,
        mock_mentee_module_filter: MagicMock,
        mock_mentee_only: MagicMock,
        mock_github_user_only: MagicMock,
        mock_module_only: MagicMock,
        mock_prefetch: MagicMock,
        api_mentorship_queries,
    ) -> None:
        """If offset is beyond available issues, expect an empty list (current behavior)."""
        mock_prefetch.return_value = MagicMock()
        mock_module = MagicMock(spec=Module, id=1)
        mock_module_only.return_value.get.return_value = mock_module

        mock_github_user = MagicMock(spec=GithubUser, id=1, login="test_mentee")
        mock_github_user_only.return_value.get.return_value = mock_github_user

        mock_mentee = MagicMock(spec=Mentee, id=2)
        mock_mentee_only.return_value.get.return_value = mock_mentee

        mock_mentee_module_filter.return_value.exists.return_value = True

        mock_issues_qs = MagicMock()
        mock_issues_qs.__getitem__.return_value = []

        mock_module_filter = (
            mock_module.issues.filter.return_value.only.return_value.prefetch_related
        )
        mock_module_filter.return_value.order_by.return_value = mock_issues_qs

        get_mentee_module_issues = api_mentorship_queries.get_mentee_module_issues
        result = get_mentee_module_issues(
            program_key="program",
            module_key="module",
            mentee_key="test_mentee",
            limit=10,
            offset=1000,
        )

        assert result == []
