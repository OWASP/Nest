from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from requests.exceptions import RequestException

from apps.github.utils import (
    check_funding_policy_compliance,
    check_owasp_site_repository,
    get_latest_invite_link_commit,
    get_repository_file_content,
    get_repository_path,
    normalize_url,
)


def make_mock_github_commit(
    sha: str,
    message: str,
    *,
    commit_date: datetime | None = None,
) -> MagicMock:
    """Build a MagicMock shaped like PyGithub ``Commit`` for invite-link commit tests."""
    commit = MagicMock()
    commit.sha = sha
    commit.commit.message = message
    commit.commit.committer.date = commit_date or datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
    return commit


class TestUtils:
    @pytest.mark.parametrize(
        ("key", "as_expected"),
        [
            ("www-chapter-abc", True),
            ("www-committee-xyz", True),
            ("www-event-123", True),
            ("www-project-abc123", True),
            ("www-random-site", False),
            ("random-prefix", False),
        ],
    )
    def test_check_owasp_site_repository(self, key, as_expected):
        assert check_owasp_site_repository(key) is as_expected

    @pytest.mark.parametrize(
        ("platform", "target", "as_expected"),
        [
            ("custom", "https://domain.owasp.org/sponsorship/", True),
            ("custom", "https://owasp.org/donate", True),
            ("github", "owasp", True),
            ("github", "OWASP", True),
            ("patreon", "", True),
            ("patreon", None, True),
            ("custom", "https://my-site.com/donate", False),
            ("custom", "https://my-site.com/owasp/donate", False),
            ("patreon", "username", False),
        ],
    )
    def test_check_funding_policy_compliance(self, platform, target, as_expected):
        assert check_funding_policy_compliance(platform, target) is as_expected

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("github.com/user/repo", None),
        ],
    )
    def test_get_repository_path(self, url, expected):
        result = get_repository_path(url)
        assert result == expected

    def test_get_repository_file_content(self, mocker):
        url = "https://example.com/file.txt"
        content = "Hello, World!"
        response = MagicMock()
        response.text = content
        mocker.patch("requests.get", return_value=response)
        result = get_repository_file_content(url)
        assert result == content

    def test_get_repository_file_content_exception(self, mocker):
        url = "https://example.com/file.txt"
        mocker.patch("requests.get", side_effect=RequestException("Test exception"))
        result = get_repository_file_content(url)
        assert result == ""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("example.com", None),
            ("invalid-url", None),
            ("https://example.com", "https://example.com"),
            ("https://example.com/path/", "https://example.com/path"),
            ("https://example.com/path#fragment", "https://example.com/path"),
            ("http://example.com", "https://example.com"),  # NOSONAR
            ("http://example.com/path", "https://example.com/path"),  # NOSONAR
            ("//example.com/path", "https://example.com/path"),
        ],
    )
    def test_normalize_url(self, url, expected):
        result = normalize_url(url)
        assert result == expected


class TestGetLatestInviteLinkCommit:
    """Tests for commit message matching (update → slack → invite, case-insensitive)."""

    @pytest.fixture
    def github(self):
        return MagicMock()

    def test_returns_newest_matching_commit(self, github):
        matching = make_mock_github_commit(
            "aaa111",
            "Update Slack invite link in slack_invite.html",
        )
        older_style = make_mock_github_commit("bbb222", "chore: noise")
        github.get_repo.return_value.get_commits.return_value = [matching, older_style]

        dt, sha = get_latest_invite_link_commit(github, repository_name="owasp/owasp.github.io")

        assert sha == "aaa111"
        assert dt == matching.commit.committer.date
        github.get_repo.assert_called_once_with("owasp/owasp.github.io")
        github.get_repo.return_value.get_commits.assert_called_once_with(
            path="_includes/slack_invite.html"
        )

    def test_skips_non_matching_until_match(self, github):
        no_invite = make_mock_github_commit("skip1", "Update Slack link only")
        wrong_order = make_mock_github_commit("skip2", "invite slack update")
        good = make_mock_github_commit("good1", "Update slack_invite.html")
        github.get_repo.return_value.get_commits.return_value = [
            no_invite,
            wrong_order,
            good,
        ]

        _, sha = get_latest_invite_link_commit(github, repository_name="o/r")

        assert sha == "good1"

    @pytest.mark.parametrize(
        "message",
        [
            "Update Slack invite link",
            "UPDATE slack INVITE",
            "chore: update slack_invite.html",
            "re-update slack stuff then invite friends",
        ],
    )
    def test_accepts_variants_with_ordered_words(self, github, message):
        c = make_mock_github_commit("sha1", message)
        github.get_repo.return_value.get_commits.return_value = [c]

        _dt, sha = get_latest_invite_link_commit(github, repository_name="o/r")

        assert sha == "sha1"

    @pytest.mark.parametrize(
        "message",
        [
            "invite update slack",
            "Slack invite update",
            "Update Slack only",
            "slack invite without update",
            "",
            "docs: readme",
        ],
    )
    def test_rejects_wrong_or_incomplete_messages(self, github, message):
        c = make_mock_github_commit("x", message)
        github.get_repo.return_value.get_commits.return_value = [c]

        dt, sha = get_latest_invite_link_commit(github, repository_name="o/r")

        assert (dt, sha) == (None, None)

    def test_returns_none_when_no_commits(self, github):
        github.get_repo.return_value.get_commits.return_value = []

        assert get_latest_invite_link_commit(github, repository_name="o/r") == (None, None)

    def test_naive_committer_date_made_aware(self, github):
        naive_dt = datetime(2025, 3, 1, 10, 0, 0)  # noqa: DTZ001
        c = make_mock_github_commit("naive1", "Update slack invite", commit_date=naive_dt)
        github.get_repo.return_value.get_commits.return_value = [c]

        dt, _sha = get_latest_invite_link_commit(github, repository_name="o/r")

        assert dt.tzinfo is not None

    def test_respects_max_commits_to_scan(self, github):
        bad = [make_mock_github_commit(f"b{i}", "wrong message") for i in range(3)]
        good = make_mock_github_commit("ok", "Update slack invite")
        github.get_repo.return_value.get_commits.return_value = [*bad, good]

        dt, sha = get_latest_invite_link_commit(
            github,
            repository_name="o/r",
            max_commits_to_scan=3,
        )

        assert dt is None
        assert sha is None
