from unittest.mock import Mock, patch

from apps.github.models.commit import Commit


class TestCommitModel:
    def test_str_representation(self):
        commit = Commit(
            sha="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
            message="Fix security vulnerability in authentication module",
        )

        result = str(commit)
        assert result.startswith("a1b2c3d:")
        assert "Fix security vulnerability in authentication module" in result

    def test_str_representation_long_message(self):
        long_message = "A" * 200
        commit = Commit(sha="abc123def456", message=long_message)
        result = str(commit)

        assert result == f"abc123d: {'A' * 100}"
        assert len(result.split(": ")[1]) == 100

    def test_str_representation_no_sha(self):
        commit = Commit(sha="", message="Test message")

        assert str(commit) == "unknown: Test message"

    def test_str_representation_no_message(self):
        commit = Commit(sha="abc123", message="")

        assert str(commit) == "abc123: No message"

    def test_meta_options(self):
        assert Commit._meta.db_table == "github_commits"
        assert Commit._meta.verbose_name_plural == "Commits"

    def test_has_indexes(self):
        indexes = Commit._meta.indexes
        assert len(indexes) >= 2

        index_fields = [tuple(index.fields) for index in indexes]
        assert ("-created_at",) in index_fields
        assert ("sha",) in index_fields

    def test_repository_field(self):
        field = Commit._meta.get_field("repository")

        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.remote_field.related_name == "commits"
        assert field.null is False

    def test_author_field(self):
        field = Commit._meta.get_field("author")

        assert field.remote_field.on_delete.__name__ == "SET_NULL"
        assert field.remote_field.related_name == "authored_commits"
        assert field.null is True
        assert field.blank is True

    def test_committer_field(self):
        field = Commit._meta.get_field("committer")

        assert field.remote_field.on_delete.__name__ == "SET_NULL"
        assert field.remote_field.related_name == "committed_commits"
        assert field.null is True
        assert field.blank is True

    def test_sha_field(self):
        field = Commit._meta.get_field("sha")

        assert field.max_length == 64

    def test_has_timestamp_fields(self):
        assert hasattr(Commit, "nest_created_at")
        assert hasattr(Commit, "nest_updated_at")
        assert hasattr(Commit, "created_at")

    def test_bulk_save(self):
        mock_commits = [Mock(id=None), Mock(id=1)]
        with patch("apps.github.models.commit.BulkSaveModel.bulk_save") as mock_bulk_save:
            Commit.bulk_save(mock_commits, fields=["message"])
            mock_bulk_save.assert_called_once_with(Commit, mock_commits, fields=["message"])
