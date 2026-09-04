"""Tests for board_activity.sync."""

from unittest.mock import Mock

import pytest
from requests.exceptions import RequestException

from apps.owasp.parsers.board_activity import sync


class TestFetchTree:
    """Tests for fetch_tree."""

    def test_returns_blob_paths_only(self, mocker):
        """Only tree entries of type=blob are returned in the path->sha map."""
        response = Mock()
        response.json.return_value = {
            "tree": [
                {"path": "a.md", "sha": "sha_a", "type": "blob"},
                {"path": "some/dir", "sha": "sha_dir", "type": "tree"},
                {"path": "b.md", "sha": "sha_b", "type": "blob"},
            ]
        }
        response.raise_for_status = Mock()
        mock_get = mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            return_value=response,
        )

        result = sync.fetch_tree()

        assert result == {"a.md": "sha_a", "b.md": "sha_b"}
        mock_get.assert_called_once()

    def test_adds_authorization_when_token_set(self, mocker):
        """GITHUB_TOKEN env var is threaded through as a Bearer header."""
        response = Mock()
        response.json.return_value = {"tree": []}
        response.raise_for_status = Mock()
        mocker.patch.dict("os.environ", {"GITHUB_TOKEN": "secret123"})
        mock_get = mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            return_value=response,
        )

        sync.fetch_tree()

        assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer secret123"

    def test_omits_authorization_when_token_absent(self, mocker):
        """No GITHUB_TOKEN means no Authorization header."""
        response = Mock()
        response.json.return_value = {"tree": []}
        response.raise_for_status = Mock()
        mocker.patch.dict("os.environ", {}, clear=True)
        mock_get = mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            return_value=response,
        )

        sync.fetch_tree()

        assert "Authorization" not in mock_get.call_args.kwargs["headers"]


class TestTargetPaths:
    """Tests for target_paths filtering logic."""

    @pytest.fixture
    def tree(self):
        return {
            "meetings/202601.md": "s1",
            "meetings/_template.meeting.md": "s2",
            "meetings-historical/2025/202508.md": "s3",
            "meetings-historical/2025/202503-18.md": "s4",
            "meetings-historical/2025/README.md": "s5",
            "meetings-historical/2024/202412.md": "s6",
            "minutes-deprecated/2020/202003.md": "s7",
            "_data/votes.yml": "s8",
            "elections/2025_elections.md": "s9",
            "attachments/foo.pdf": "s10",
        }

    def test_yields_only_meeting_markdown_files(self, tree):
        """Upcoming meetings/, non-meeting files, non-.md, non-YYYYMM names are filtered out."""
        result = set(sync.target_paths(tree))

        assert result == {
            "meetings-historical/2025/202508.md",
            "meetings-historical/2025/202503-18.md",
            "meetings-historical/2024/202412.md",
            "minutes-deprecated/2020/202003.md",
        }

    def test_filters_by_year(self, tree):
        """--year restricts to files with matching 4-digit prefix."""
        result = set(sync.target_paths(tree, year=2025))

        assert result == {
            "meetings-historical/2025/202508.md",
            "meetings-historical/2025/202503-18.md",
        }

    def test_filters_by_year_and_month(self, tree):
        """--year + --month restricts to YYYYMM prefix."""
        result = set(sync.target_paths(tree, year=2025, month=8))

        assert result == {"meetings-historical/2025/202508.md"}

    def test_single_path_short_circuits(self, tree):
        """Passing --path returns that path only when present in the tree."""
        result = list(sync.target_paths(tree, path="meetings-historical/2025/202508.md"))

        assert result == ["meetings-historical/2025/202508.md"]

    def test_single_path_absent_yields_nothing(self, tree):
        """Missing --path yields no results."""
        result = list(sync.target_paths(tree, path="nonexistent.md"))

        assert result == []

    @pytest.mark.parametrize("year", [1, 202, 10000])
    def test_rejects_non_four_digit_year(self, tree, year):
        """Year outside 1000-9999 is rejected so short prefixes don't match multiple years."""
        with pytest.raises(ValueError, match="4-digit"):
            list(sync.target_paths(tree, year=year))


class TestFetchFileContent:
    """Tests for fetch_file_content status handling."""

    def test_returns_text_on_2xx(self, mocker):
        """A 200 response returns the body text."""
        response = Mock(ok=True, status_code=200, text="hello")
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            return_value=response,
        )

        assert sync.fetch_file_content("p.md") == "hello"

    @pytest.mark.parametrize("status", [403, 404, 500, 502])
    def test_returns_empty_on_non_2xx(self, mocker, status):
        """A non-2xx response returns empty string so error body is not fed to the LLM."""
        response = Mock(ok=False, status_code=status, text="error body")
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            return_value=response,
        )

        assert sync.fetch_file_content("p.md") == ""

    def test_returns_empty_on_request_exception(self, mocker):
        """A connection error returns empty string rather than propagating."""
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.requests.get",
            side_effect=RequestException("boom"),
        )

        assert sync.fetch_file_content("p.md") == ""


class TestSyncFile:
    """Tests for sync_file per-file behavior."""

    def test_unchanged_when_checksum_matches(self, mocker):
        """Existing meeting with matching blob SHA is skipped."""
        existing = Mock(source_checksum="abc")
        mock_qs = Mock()
        mock_qs.first.return_value = existing
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mock_fetch = mocker.patch("apps.owasp.parsers.board_activity.sync.fetch_file_content")

        result = sync.sync_file("meetings/202601.md", "abc")

        assert result == sync.SyncStatus.UNCHANGED
        mock_fetch.assert_not_called()

    def test_force_reparses_even_when_checksum_matches(self, mocker):
        """--force triggers a re-parse regardless of checksum."""
        existing = Mock(source_checksum="abc")
        mock_qs = Mock()
        mock_qs.first.return_value = existing
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_file_content",
            return_value="markdown content",
        )
        client = Mock()
        client.set_prompt.return_value = client
        client.set_input.return_value = client
        client.parse.return_value = Mock()
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.OpenAi",
            return_value=client,
        )
        mocker.patch("apps.owasp.parsers.board_activity.sync.translator.upsert")

        result = sync.sync_file("p.md", "abc", force=True)

        assert result == sync.SyncStatus.UPDATED

    def test_empty_content_skips(self, mocker):
        """Empty fetch response yields SKIPPED without an LLM call."""
        mock_qs = Mock()
        mock_qs.first.return_value = None
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mocker.patch("apps.owasp.parsers.board_activity.sync.fetch_file_content", return_value="")
        mock_openai = mocker.patch("apps.owasp.parsers.board_activity.sync.OpenAi")

        result = sync.sync_file("p.md", "sha")

        assert result == sync.SyncStatus.SKIPPED
        mock_openai.assert_not_called()

    def test_llm_failure_yields_errored(self, mocker):
        """LLM returning None yields ERRORED and skips DB writes."""
        mock_qs = Mock()
        mock_qs.first.return_value = None
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_file_content",
            return_value="content",
        )
        client = Mock()
        client.set_prompt.return_value = client
        client.set_input.return_value = client
        client.parse.return_value = None
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.OpenAi",
            return_value=client,
        )
        mock_upsert = mocker.patch("apps.owasp.parsers.board_activity.sync.translator.upsert")

        result = sync.sync_file("p.md", "sha")

        assert result == sync.SyncStatus.ERRORED
        mock_upsert.assert_not_called()

    def test_dry_run_parses_but_does_not_upsert(self, mocker):
        """--dry-run runs the LLM but skips the DB write."""
        mock_qs = Mock()
        mock_qs.first.return_value = None
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_file_content",
            return_value="content",
        )
        parsed = Mock()
        parsed.model_dump_json.return_value = "{}"
        client = Mock()
        client.set_prompt.return_value = client
        client.set_input.return_value = client
        client.parse.return_value = parsed
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.OpenAi",
            return_value=client,
        )
        mock_upsert = mocker.patch("apps.owasp.parsers.board_activity.sync.translator.upsert")

        result = sync.sync_file("p.md", "sha", dry_run=True)

        assert result == sync.SyncStatus.WOULD_UPDATE
        mock_upsert.assert_not_called()

    def test_new_meeting_returns_created(self, mocker):
        """Meeting not previously in DB returns CREATED after upsert."""
        mock_qs = Mock()
        mock_qs.first.return_value = None
        mocker.patch(
            "apps.owasp.models.board_meeting.BoardMeeting.objects.filter",
            return_value=mock_qs,
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_file_content",
            return_value="content",
        )
        client = Mock()
        client.set_prompt.return_value = client
        client.set_input.return_value = client
        client.parse.return_value = Mock()
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.OpenAi",
            return_value=client,
        )
        mocker.patch("apps.owasp.parsers.board_activity.sync.translator.upsert")

        result = sync.sync_file("p.md", "sha")

        assert result == sync.SyncStatus.CREATED


class TestRun:
    """Tests for the top-level run function."""

    def test_returns_errored_when_tree_fetch_fails(self, mocker):
        """Tree fetch RequestException is caught and recorded as ERRORED."""
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_tree",
            side_effect=RequestException("boom"),
        )

        stats = sync.run()

        assert stats.counts == {sync.SyncStatus.ERRORED: 1}

    def test_aggregates_status_counts_across_files(self, mocker):
        """Per-file statuses are aggregated in SyncStats.counts."""
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_tree",
            return_value={
                "meetings-historical/2025/202501.md": "s1",
                "meetings-historical/2025/202502.md": "s2",
                "meetings-historical/2025/202503.md": "s3",
            },
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.sync_file",
            side_effect=[
                sync.SyncStatus.CREATED,
                sync.SyncStatus.UNCHANGED,
                sync.SyncStatus.CREATED,
            ],
        )

        stats = sync.run(year=2025)

        assert stats.counts == {
            sync.SyncStatus.CREATED: 2,
            sync.SyncStatus.UNCHANGED: 1,
        }

    def test_sync_file_exception_is_recorded_as_errored(self, mocker):
        """A per-file exception is caught and recorded as ERRORED without aborting."""
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.fetch_tree",
            return_value={"meetings-historical/2025/202501.md": "s1"},
        )
        mocker.patch(
            "apps.owasp.parsers.board_activity.sync.sync_file",
            side_effect=RuntimeError("bad"),
        )

        stats = sync.run(year=2025)

        assert stats.counts == {sync.SyncStatus.ERRORED: 1}
