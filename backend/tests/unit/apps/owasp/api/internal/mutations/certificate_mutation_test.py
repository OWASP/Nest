"""Tests for OWASP certificate GraphQL mutations."""

from unittest.mock import MagicMock, patch

import pytest
from graphql import GraphQLError
from pydantic import ValidationError

from apps.owasp.api.internal.mutations.certificate import (
    CertificateMutation,
    IssueCertificateSchema,
)


@pytest.fixture(autouse=True)
def _mock_transaction_atomic():
    """Disable transaction.atomic decorator for all tests."""
    with (
        patch("django.db.transaction.Atomic.__enter__", return_value=None),
        patch("django.db.transaction.Atomic.__exit__", return_value=False),
    ):
        yield


@pytest.fixture
def mutation():
    return CertificateMutation()


def _make_info(*, is_project_leader=False, has_chapters=False):
    """Return a mock strawberry Info with a configured user."""
    info = MagicMock()
    user = MagicMock()
    info.context.request.user = user
    gh = MagicMock()
    gh.is_project_leader = is_project_leader
    chapters_qs = MagicMock()
    chapters_qs.exists.return_value = has_chapters
    gh.chapters = chapters_qs
    user.github_user = gh
    return info


def _make_input(**overrides):
    """Return a mock IssueCertificateInput with sensible defaults."""
    defaults = {
        "recipient_login": "alice",
        "recipient_logins": None,
        "title": "Contributor Award",
        "message": "Thank you!",
        "project_key": "www-project-juice-shop",
        "chapter_key": None,
    }
    defaults.update(overrides)
    return MagicMock(**defaults)


class TestIssueCertificateSchema:
    """Tests for IssueCertificateSchema model validator."""

    def test_single_recipient_login_accepted(self):
        """A single recipient_login should be converted into recipient_logins."""
        schema = IssueCertificateSchema(
            recipient_login="alice",
            title="Award",
            project_key="juice-shop",
        )
        assert schema.recipient_logins == ["alice"]

    def test_duplicate_logins_are_deduplicated(self):
        """Duplicate logins (case-insensitive) must appear only once."""
        schema = IssueCertificateSchema(
            recipient_logins=["Alice", "alice", "ALICE"],
            title="Award",
            project_key="juice-shop",
        )
        assert len(schema.recipient_logins) == 1
        assert schema.recipient_logins[0] == "Alice"

    def test_empty_string_logins_are_dropped(self):
        """Empty / whitespace-only strings in recipient_logins must be dropped."""
        schema = IssueCertificateSchema(
            recipient_logins=["alice", "  ", ""],
            title="Award",
            project_key="juice-shop",
        )
        assert schema.recipient_logins == ["alice"]

    def test_no_recipient_raises_value_error(self):
        """Omitting both recipient fields must raise ValidationError."""
        with pytest.raises(ValidationError, match="Recipient login cannot be empty"):
            IssueCertificateSchema(title="Award", project_key="juice-shop")

    def test_title_too_long_raises_validation_error(self):
        """Title exceeding MAX_TITLE_LENGTH must raise ValidationError."""
        with pytest.raises(ValidationError):
            IssueCertificateSchema(
                recipient_login="alice",
                title="x" * 51,
                project_key="juice-shop",
            )

    def test_message_too_long_raises_validation_error(self):
        """Message exceeding MAX_MESSAGE_LENGTH must raise ValidationError."""
        with pytest.raises(ValidationError):
            IssueCertificateSchema(
                recipient_login="alice",
                title="Award",
                message="x" * 281,
                project_key="juice-shop",
            )

    def test_project_key_prefix_removed(self):
        """www-project- prefix must be stripped from project_key."""
        schema = IssueCertificateSchema(
            recipient_login="alice",
            title="Award",
            project_key="www-project-juice-shop",
        )
        assert schema.project_key == "juice-shop"

    def test_chapter_key_prefix_removed(self):
        """www-chapter- prefix must be stripped from chapter_key."""
        schema = IssueCertificateSchema(
            recipient_login="alice",
            title="Award",
            chapter_key="www-chapter-london",
        )
        assert schema.chapter_key == "london"

    def test_both_project_and_chapter_raises_value_error(self):
        """Providing both project_key and chapter_key must raise ValidationError."""
        with pytest.raises(ValidationError, match="Provide either project or chapter, not both"):
            IssueCertificateSchema(
                recipient_login="alice",
                title="Award",
                project_key="juice-shop",
                chapter_key="london",
            )

    def test_neither_project_nor_chapter_raises_value_error(self):
        """Omitting both project_key and chapter_key must raise ValidationError."""
        with pytest.raises(ValidationError, match="Either project or chapter must be provided"):
            IssueCertificateSchema(
                recipient_login="alice",
                title="Award",
            )


class TestIssueCertificateMutation:
    """Tests for CertificateMutation.issue_certificate."""

    def test_no_github_user_raises_forbidden(self, mutation):
        """Users without a linked github_user should get FORBIDDEN."""
        info = MagicMock()
        info.context.request.user.github_user = None
        input_data = _make_input()

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "FORBIDDEN"

    def test_not_leader_or_chapter_leader_raises_forbidden(self, mutation):
        """Users who are neither project nor chapter leaders should get FORBIDDEN."""
        info = _make_info(is_project_leader=False, has_chapters=False)
        input_data = _make_input()

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "FORBIDDEN"

    def test_validation_error_raises_graphql_validation_error(self, mutation):
        """ValidationError during schema construction produces VALIDATION_ERROR."""
        info = _make_info(is_project_leader=True)
        bad_input = _make_input(title="", recipient_login="alice", project_key="juice-shop")

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, bad_input)

        assert exc_info.value.extensions["code"] == "VALIDATION_ERROR"

    @patch("apps.owasp.api.internal.mutations.certificate.Project")
    def test_project_not_found_raises_graphql_not_found(self, mock_project, mutation):
        """A missing project should raise GraphQLError with NOT_FOUND."""
        mock_project.DoesNotExist = Exception
        mock_project.objects.get.side_effect = mock_project.DoesNotExist("not found")

        info = _make_info(is_project_leader=True)
        input_data = _make_input(project_key="www-project-missing", chapter_key=None)

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "NOT_FOUND"
        assert exc_info.value.extensions["field"] == "projectKey"

    @patch("apps.owasp.api.internal.mutations.certificate.Chapter")
    def test_chapter_not_found_raises_graphql_not_found(self, mock_chapter, mutation):
        """A missing chapter should raise GraphQLError with NOT_FOUND."""
        mock_chapter.DoesNotExist = Exception
        mock_chapter.objects.get.side_effect = mock_chapter.DoesNotExist("not found")

        info = _make_info(is_project_leader=True)
        input_data = _make_input(project_key=None, chapter_key="www-chapter-missing")

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "NOT_FOUND"
        assert exc_info.value.extensions["field"] == "chapterKey"

    @patch("apps.owasp.api.internal.mutations.certificate.GithubUser")
    @patch("apps.owasp.api.internal.mutations.certificate.Project")
    def test_single_missing_recipient_raises_not_found(self, mock_project, mock_gh_user, mutation):
        """When a recipient login is not found, raise NOT_FOUND."""
        mock_project.objects.get.return_value = MagicMock()
        mock_gh_user.objects.filter.return_value = []

        info = _make_info(is_project_leader=True)
        input_data = _make_input(recipient_login="ghost", project_key="www-project-juice-shop")

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "NOT_FOUND"
        assert exc_info.value.extensions["field"] == "recipientLogins"
        assert "ghost" in exc_info.value.message

    @patch("apps.owasp.api.internal.mutations.certificate.GithubUser")
    @patch("apps.owasp.api.internal.mutations.certificate.Project")
    def test_partial_recipients_missing_raises_not_found(
        self, mock_project, mock_gh_user, mutation
    ):
        """When only some recipients are missing the NOT_FOUND error still fires."""
        mock_project.objects.get.return_value = MagicMock()

        found_user = MagicMock()
        found_user.login = "alice"
        mock_gh_user.objects.filter.return_value = [found_user]

        info = _make_info(is_project_leader=True)
        input_data = _make_input(
            recipient_login=None,
            recipient_logins=["alice", "ghost"],
            project_key="www-project-juice-shop",
        )

        with pytest.raises(GraphQLError) as exc_info:
            mutation.issue_certificate(info, input_data)

        assert exc_info.value.extensions["code"] == "NOT_FOUND"
        assert "ghost" in exc_info.value.message

    @patch("apps.owasp.api.internal.mutations.certificate.Certificate")
    @patch("apps.owasp.api.internal.mutations.certificate.GithubUser")
    @patch("apps.owasp.api.internal.mutations.certificate.Project")
    def test_successful_certificate_issuance_with_project(
        self, mock_project, mock_gh_user, mock_cert, mutation
    ):
        """Happy path: issue a certificate linked to a project."""
        mock_proj_obj = MagicMock()
        mock_project.objects.get.return_value = mock_proj_obj

        recipient = MagicMock()
        recipient.login = "alice"
        mock_gh_user.objects.filter.return_value = [recipient]

        cert = MagicMock()
        mock_cert.objects.create.return_value = cert

        info = _make_info(is_project_leader=True)
        result = mutation.issue_certificate(
            info,
            _make_input(
                recipient_login="alice",
                title="Contributor Award",
                message="Thank you!",
                project_key="www-project-juice-shop",
                chapter_key=None,
            ),
        )

        assert result == [cert]
        mock_cert.objects.create.assert_called_once_with(
            recipient=recipient,
            issuer=info.context.request.user.github_user,
            title="Contributor Award",
            message="Thank you!",
            project=mock_proj_obj,
            chapter=None,
        )

    @patch("apps.owasp.api.internal.mutations.certificate.Certificate")
    @patch("apps.owasp.api.internal.mutations.certificate.GithubUser")
    @patch("apps.owasp.api.internal.mutations.certificate.Chapter")
    def test_successful_certificate_issuance_with_chapter(
        self, mock_chapter, mock_gh_user, mock_cert, mutation
    ):
        """Happy path: issue a certificate linked to a chapter."""
        mock_chap_obj = MagicMock()
        mock_chapter.objects.get.return_value = mock_chap_obj

        recipient = MagicMock()
        recipient.login = "bob"
        mock_gh_user.objects.filter.return_value = [recipient]

        cert = MagicMock()
        mock_cert.objects.create.return_value = cert

        info = _make_info(is_project_leader=False, has_chapters=True)
        result = mutation.issue_certificate(
            info,
            _make_input(
                recipient_login="bob",
                title="Chapter Leader Award",
                message="Thank you!",
                project_key=None,
                chapter_key="www-chapter-london",
            ),
        )

        assert result == [cert]
        mock_cert.objects.create.assert_called_once_with(
            recipient=recipient,
            issuer=info.context.request.user.github_user,
            title="Chapter Leader Award",
            message="Thank you!",
            project=None,
            chapter=mock_chap_obj,
        )
