from unittest.mock import Mock, patch

from apps.github.models.commit import Commit
from apps.github.models.repository import Repository
from apps.github.models.user import User


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

    @patch("apps.github.models.commit.Commit.get_node_id", return_value="test_node_id")
    @patch("apps.github.models.commit.Commit.objects.get")
    def test_update_data_creates_new_commit(self, mock_get, mock_get_node_id):
        mock_get.side_effect = Commit.DoesNotExist
        mock_gh_commit = Mock()
        mock_gh_commit.sha = "test_sha"
        mock_gh_commit.commit.message = "Test message"
        mock_gh_commit.commit.author.date = "2023-01-01T00:00:00Z"

        mock_repository = Repository(id=1)
        mock_author = User(id=1)
        mock_committer = User(id=2)

        with patch("apps.github.models.commit.Commit.save") as mock_save:
            commit = Commit.update_data(
                gh_commit=mock_gh_commit,
                repository=mock_repository,
                author=mock_author,
                committer=mock_committer,
            )

            mock_get_node_id.assert_called_once_with(mock_gh_commit)
            mock_get.assert_called_once_with(node_id="test_node_id")
            mock_save.assert_called_once()


    @patch("apps.github.models.commit.Commit.get_node_id", return_value="test_node_id")
    @patch("apps.github.models.commit.Commit.objects.get")
    def test_update_data_updates_existing_commit(self, mock_get, mock_get_node_id):
        mock_existing_commit = Commit(node_id="test_node_id")
        mock_get.return_value = mock_existing_commit

        mock_gh_commit = Mock()
        mock_gh_commit.sha = "new_sha"
        mock_gh_commit.commit.message = "New message"
        mock_gh_commit.commit.author.date = "2024-01-01T00:00:00Z"

        mock_repository = Repository(id=1)
        mock_author = User(id=1)
        mock_committer = User(id=2)

        with patch("apps.github.models.commit.Commit.save") as mock_save:
            commit = Commit.update_data(
                gh_commit= mock_gh_commit,
                repository=mock_repository,
                author=mock_author,
                committer=mock_committer,
            )

            mock_get_node_id.assert_called_once_with(mock_gh_commit)
            mock_get.assert_called_once_with(node_id="test_node_id")
            assert commit == mock_existing_commit
            assert commit.sha == "new_sha"
            assert commit.message == "New message"
            assert commit.created_at == "2024-01-01T00:00:00Z"
            mock_save.assert_called_once()


    @patch("apps.github.models.commit.Commit.get_node_id", return_value="test_node_id")
    @patch("apps.github.models.commit.Commit.objects.get")
    def test_update_data_with_save_false(self, mock_get, mock_get_node_id):
        mock_get.side_effect = Commit.DoesNotExist
        mock_gh_commit = Mock()
        mock_gh_commit.sha = "test_sha"
        mock_gh_commit.commit.message = "Test message"
        mock_gh_commit.commit.author.date = "2023-01-01T00:00:00Z"

        mock_repository = Repository(id=1)
        mock_author = User(id=1)
        mock_committer = User(id=2)

        with patch("apps.github.models.commit.Commit.save") as mock_save:
            commit = Commit.update_data(
                gh_commit=mock_gh_commit,
                repository=mock_repository,
                author=mock_author,
                committer=mock_committer,
                save=False,
            )
            mock_get_node_id.assert_called_once_with(mock_gh_commit)
            mock_get.assert_called_once_with(node_id="test_node_id")
            mock_save.assert_not_called()

